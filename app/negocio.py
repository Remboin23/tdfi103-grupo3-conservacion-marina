from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.db import get_engine, run_query


# ============================================================================
# 1. AUTENTICACIÓN Y PERMISOS (Control de Usuarios)
# ============================================================================
def autenticar_usuario(username: str, password: str) -> dict | None:
    sql = """
        SELECT
            cu.idCuenta,
            cu.nombreUsuario,
            t.nombreCompleto,
            t.cargo,
            r.nombreRol
        FROM cuenta_usuario cu
        JOIN trabajador t ON cu.rutTrabajador = t.rutTrabajador
        JOIN usuario_rol ur ON cu.idCuenta = ur.idCuenta
        JOIN rol r ON ur.idRol = r.idRol
        WHERE cu.nombreUsuario = :u
          AND cu.passwordHash = :p
          AND cu.activa = TRUE
        LIMIT 1
    """
    rows = run_query(sql, {"u": username.strip(), "p": password.strip()})
    if not rows:
        return None

    user_info = rows[0]
    perm_sql = """
        SELECT DISTINCT rp.permiso
        FROM usuario_rol ur
        JOIN rol_permiso rp ON ur.idRol = rp.idRol
        WHERE ur.idCuenta = :cid
    """
    perms = run_query(perm_sql, {"cid": user_info["idCuenta"]})
    user_info["permisos"] = [p["permiso"] for p in perms]
    return user_info


# ============================================================================
# 2. FORMULARIO TRANSACCIONAL (Reserva / Participación)
# ============================================================================
def listar_visitantes() -> list[dict]:
    return run_query("""
        SELECT idVisitante, CONCAT(nombres, ' ', apellidoP, ' ', apellidoM, ' (', correoPersonal, ')') AS etiqueta
        FROM visitante
        ORDER BY apellidoP, nombres
    """)


def listar_actividades_disponibles() -> list[dict]:
    return run_query("""
        SELECT
            a.idActividad,
            CONCAT(
                c.nombre, ' | Sector ', a.numeroInterno,
                ' | ', a.tipoActividad,
                ' (', a.fechaProgramada, ' ', a.horaInicio, ')'
            ) AS etiqueta,
            a.cupoMaximo,
            (SELECT COUNT(*) FROM participacion p WHERE p.idActividad = a.idActividad) AS inscritosActuales
        FROM actividad a
        JOIN centro_conservacion c ON a.codigoCentro = c.codigoCentro
        WHERE c.activo = TRUE
        ORDER BY a.fechaProgramada DESC
    """)


def registrar_participacion_transaccional(id_visitante: int, id_actividad: int, asistencia: bool) -> tuple[bool, str]:
    engine = get_engine()
    try:
        with engine.begin() as conn:
            # 1. Bloquear fila de actividad para validar cupo en concurrencia
            act = conn.execute(
                text("SELECT cupoMaximo FROM actividad WHERE idActividad = :aid FOR UPDATE"),
                {"aid": id_actividad},
            ).fetchone()
            if not act:
                return False, "La actividad seleccionada no existe."

            # 2. Verificar duplicado
            dup = conn.execute(
                text("SELECT 1 FROM participacion WHERE idVisitante = :vid AND idActividad = :aid"),
                {"vid": id_visitante, "aid": id_actividad},
            ).fetchone()
            if dup:
                return False, "El visitante ya tiene una reserva registrada en esta actividad."

            # 3. Verificar cupo disponible
            inscritos = conn.execute(
                text("SELECT COUNT(*) FROM participacion WHERE idActividad = :aid"),
                {"aid": id_actividad},
            ).scalar()
            if inscritos >= act[0]:
                return False, f"Cupo completo ({inscritos}/{act[0]} participantes)."

            # 4. Insertar participación
            conn.execute(
                text("""
                    INSERT INTO participacion (idVisitante, idActividad, fechaRegistro, asistencia)
                    VALUES (:vid, :aid, NOW(), :asis)
                """),
                {"vid": id_visitante, "aid": id_actividad, "asis": asistencia},
            )
        return True, "Participación/reserva registrada exitosamente con integridad referencial."
    except SQLAlchemyError as e:
        return False, f"Error de base de datos (transacción revertida): {str(e)}"


# ============================================================================
# 3. CRUD DE TABLAS MAESTRAS (CENTRO_CONSERVACION Y ESPECIE_MARINA)
# ============================================================================
def listar_regiones() -> list[dict]:
    return run_query("SELECT codigoRegion, nombreOficial FROM region_maritima ORDER BY nombreOficial")


def listar_centros() -> list[dict]:
    return run_query("""
        SELECT
            c.codigoCentro, c.nombre, c.fechaCreacion, c.superficieProtegida,
            c.ubicacion, c.presupuesto, c.capacidadOperativa, c.estadoConservacion,
            c.codigoRegion, r.nombreOficial AS region, c.activo
        FROM centro_conservacion c
        JOIN region_maritima r ON c.codigoRegion = r.codigoRegion
        ORDER BY c.codigoCentro
    """)


def crear_centro(datos: dict) -> tuple[bool, str]:
    engine = get_engine()
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO centro_conservacion
                    (codigoCentro, nombre, fechaCreacion, superficieProtegida, ubicacion, presupuesto, capacidadOperativa, estadoConservacion, codigoRegion, activo)
                    VALUES (:codigo, :nombre, :fecha, :superficie, :ubicacion, :presupuesto, :capacidad, :estado, :region, TRUE)
                """),
                datos,
            )
        return True, "Centro de conservación creado correctamente."
    except SQLAlchemyError as e:
        return False, f"Error al crear centro: {str(e)}"


def actualizar_centro(datos: dict) -> tuple[bool, str]:
    engine = get_engine()
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    UPDATE centro_conservacion
                    SET nombre = :nombre,
                        ubicacion = :ubicacion,
                        presupuesto = :presupuesto,
                        capacidadOperativa = :capacidad,
                        estadoConservacion = :estado
                    WHERE codigoCentro = :codigo
                """),
                datos,
            )
        return True, "Centro actualizado correctamente."
    except SQLAlchemyError as e:
        return False, f"Error al actualizar centro: {str(e)}"


def cambiar_estado_centro(codigo: str, activo: bool) -> tuple[bool, str]:
    engine = get_engine()
    try:
        with engine.begin() as conn:
            conn.execute(
                text("UPDATE centro_conservacion SET activo = :act WHERE codigoCentro = :cod"),
                {"act": activo, "cod": codigo},
            )
        accion = "reactivado" if activo else "desactivado lógicamente"
        return True, f"Centro {codigo} {accion} correctamente."
    except SQLAlchemyError as e:
        return False, f"Error al cambiar estado del centro: {str(e)}"


def listar_especies() -> list[dict]:
    return run_query("""
        SELECT
            e.codigoEspecie, e.nombreCientifico, e.nombreComun,
            e.estadoConservacion, e.fechaIncorporacion, e.distribucionGeografica, e.activo,
            CASE
                WHEN p.codigoEspecie IS NOT NULL THEN 'Pez'
                WHEN mm.codigoEspecie IS NOT NULL THEN 'Mamífero Marino'
                WHEN co.codigoEspecie IS NOT NULL THEN 'Coral'
                ELSE 'No Clasificada'
            END AS clasificacion
        FROM especie_marina e
        LEFT JOIN pez p ON e.codigoEspecie = p.codigoEspecie
        LEFT JOIN mamifero_marino mm ON e.codigoEspecie = mm.codigoEspecie
        LEFT JOIN coral co ON e.codigoEspecie = co.codigoEspecie
        ORDER BY e.codigoEspecie
    """)


def crear_especie(datos: dict) -> tuple[bool, str]:
    engine = get_engine()
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO especie_marina
                    (codigoEspecie, nombreCientifico, nombreComun, estadoConservacion, fechaIncorporacion, distribucionGeografica, activo)
                    VALUES (:codigo, :cientifico, :comun, :estado, :fecha, :distribucion, TRUE)
                """),
                datos,
            )
        return True, "Especie marina registrada correctamente."
    except SQLAlchemyError as e:
        return False, f"Error al registrar especie: {str(e)}"


def actualizar_especie(datos: dict) -> tuple[bool, str]:
    engine = get_engine()
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    UPDATE especie_marina
                    SET nombreComun = :comun,
                        estadoConservacion = :estado,
                        distribucionGeografica = :distribucion
                    WHERE codigoEspecie = :codigo
                """),
                datos,
            )
        return True, "Especie marina actualizada correctamente."
    except SQLAlchemyError as e:
        return False, f"Error al actualizar especie: {str(e)}"


def cambiar_estado_especie(codigo: str, activo: bool) -> tuple[bool, str]:
    engine = get_engine()
    try:
        with engine.begin() as conn:
            conn.execute(
                text("UPDATE especie_marina SET activo = :act WHERE codigoEspecie = :cod"),
                {"act": activo, "cod": codigo},
            )
        accion = "reactivada" if activo else "desactivada lógicamente"
        return True, f"Especie {codigo} {accion} correctamente."
    except SQLAlchemyError as e:
        return False, f"Error al cambiar estado de la especie: {str(e)}"


# ============================================================================
# 4. CONSULTAS INDEPENDIENTES PARA EL DASHBOARD (3 Fase 1 + 1 Propuesta)
# ============================================================================
def dash_q1_sectores_actividad(codigo_centro: str, f_ini: str, f_fin: str) -> list[dict]:
    sql = """
        SELECT
            CONCAT(c.nombre, ' - ', s.nombre) AS sector,
            COUNT(DISTINCT a.idActividad) AS actividades,
            COUNT(p.idVisitante) AS visitantes
        FROM centro_conservacion c
        JOIN sector_marino s ON c.codigoCentro = s.codigoCentro
        JOIN actividad a ON s.codigoCentro = a.codigoCentro AND s.numeroInterno = a.numeroInterno
        LEFT JOIN participacion p ON a.idActividad = p.idActividad
        WHERE a.fechaProgramada BETWEEN :fini AND :ffin
          AND (:centro = 'TODOS' OR c.codigoCentro = :centro)
        GROUP BY c.nombre, s.nombre
        ORDER BY visitantes DESC, actividades DESC
        LIMIT 12
    """
    return run_query(sql, {"centro": codigo_centro, "fini": f_ini, "ffin": f_fin})


def dash_q2_distribucion_especies(codigo_centro: str) -> list[dict]:
    sql = """
        SELECT
            CASE
                WHEN p.codigoEspecie IS NOT NULL THEN 'Pez'
                WHEN mm.codigoEspecie IS NOT NULL THEN 'Mamífero Marino'
                WHEN co.codigoEspecie IS NOT NULL THEN 'Coral'
                ELSE 'No Clasificada'
            END AS tipo,
            COUNT(DISTINCT e.codigoEspecie) AS especiesDistintas,
            SUM(m.cantidadObservada) AS ejemplaresObservados
        FROM monitoreo_especie m
        JOIN especie_marina e ON m.codigoEspecie = e.codigoEspecie
        LEFT JOIN pez p ON e.codigoEspecie = p.codigoEspecie
        LEFT JOIN mamifero_marino mm ON e.codigoEspecie = mm.codigoEspecie
        LEFT JOIN coral co ON e.codigoEspecie = co.codigoEspecie
        WHERE (:centro = 'TODOS' OR m.codigoCentro = :centro)
        GROUP BY tipo
        ORDER BY ejemplaresObservados DESC
    """
    return run_query(sql, {"centro": codigo_centro})


def dash_q3_participantes_evaluacion(codigo_centro: str) -> list[dict]:
    sql = """
        SELECT
            c.nombre AS centro,
            s.nombre AS sector,
            a.idActividad,
            a.tipoActividad,
            COUNT(DISTINCT p.idVisitante) AS participantes,
            ROUND(AVG(ev.calificacion), 2) AS evaluacionPromedio
        FROM actividad a
        JOIN sector_marino s ON a.codigoCentro = s.codigoCentro AND a.numeroInterno = s.numeroInterno
        JOIN centro_conservacion c ON s.codigoCentro = c.codigoCentro
        JOIN participacion p ON a.idActividad = p.idActividad
        JOIN evaluacion ev ON a.idActividad = ev.idActividad
        WHERE (:centro = 'TODOS' OR c.codigoCentro = :centro)
        GROUP BY c.nombre, s.nombre, a.idActividad, a.tipoActividad
    """
    return run_query(sql, {"centro": codigo_centro})


def dash_q4_monitoreo_estado_conservacion(codigo_region: str) -> list[dict]:
    sql = """
        SELECT
            DATE_FORMAT(m.fecha, '%Y-%m') AS mes,
            e.estadoConservacion,
            SUM(m.cantidadObservada) AS totalObservados
        FROM monitoreo_especie m
        JOIN especie_marina e ON m.codigoEspecie = e.codigoEspecie
        JOIN centro_conservacion c ON m.codigoCentro = c.codigoCentro
        WHERE (:region = 'TODAS' OR c.codigoRegion = :region)
        GROUP BY mes, e.estadoConservacion
        ORDER BY mes ASC
    """
    return run_query(sql, {"region": codigo_region})