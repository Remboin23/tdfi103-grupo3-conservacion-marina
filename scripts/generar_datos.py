import os
import random
from datetime import date, datetime, time, timedelta
from faker import Faker

# Semilla fija para garantizar reproducibilidad (exigencia de la rúbrica)
SEED = 202603
random.seed(SEED)
fake = Faker("es_CL")
Faker.seed(SEED)

OUTPUT_SQL = os.path.join("sql", "02_insert_datos.sql")


def sql_str(val):
    if val is None:
        return "NULL"
    escaped = str(val).replace("'", "''")
    return f"'{escaped}'"


def main():
    os.makedirs("sql", exist_ok=True)
    lines = [
        "-- ============================================================================",
        "-- POBLAMIENTO SINTÉTICO REPRODUCIBLE - GRUPO 3 (CASO 3: CONSERVACIÓN MARINA)",
        f"-- Semilla utilizada: {SEED}",
        "-- ============================================================================",
        "USE conservacion_marina;",
        "SET FOREIGN_KEY_CHECKS = 0;",
        "",
    ]

    # 1. REGIONES MARÍTIMAS (5 a 10 -> generamos 7)
    regiones_nombres = [
        "Región Marítima Norte Grande",
        "Región Marítima Atacama-Coquimbo",
        "Región Marítima Valparaíso Central",
        "Región Marítima Juan Fernández e Islas Desventuradas",
        "Región Marítima Biobío-Araucanía",
        "Región Marítima Chiloé y Fiordos Norte",
        "Región Marítima Patagonia y Canales Australes",
    ]
    niveles_prot = ["Bajo", "Medio", "Alto", "Estricto"]
    regiones = []
    lines.append("-- 1. REGION_MARITIMA")
    for idx, nombre in enumerate(regiones_nombres, start=1):
        cod = f"REG-{idx:02d}"
        sup = round(random.uniform(15000.0, 250000.0), 2)
        pres = round(random.uniform(50000000.0, 450000000.0), 2)
        nivel = niveles_prot[(idx - 1) % len(niveles_prot)]
        regiones.append(cod)
        lines.append(
            f"INSERT INTO region_maritima (codigoRegion, nombreOficial, superficieProtegida, presupuestoAnual, nivelProteccionAmbiental) "
            f"VALUES ({sql_str(cod)}, {sql_str(nombre)}, {sup}, {pres}, {sql_str(nivel)});"
        )
    lines.append("")

    # 2. CENTROS DE CONSERVACIÓN (12 a 20 -> generamos 15)
    estados_centro = ["Óptimo", "Estable", "En Recuperación", "Crítico"]
    centros = []
    lines.append("-- 2. CENTRO_CONSERVACION")
    for idx in range(1, 16):
        cod = f"CEN-{idx:03d}"
        nombre = f"Centro Marino {fake.city()} #{idx}"
        f_creacion = fake.date_between(start_date="-15y", end_date="-1y")
        sup = round(random.uniform(500.0, 18000.0), 2)
        ubicacion = f"Costa de {fake.city()}, Chile"
        pres = round(random.uniform(15000000.0, 95000000.0), 2)
        cap = random.randint(40, 250)
        estado = random.choice(estados_centro)
        cod_reg = random.choice(regiones)
        centros.append(cod)
        lines.append(
            f"INSERT INTO centro_conservacion (codigoCentro, nombre, fechaCreacion, superficieProtegida, ubicacion, presupuesto, capacidadOperativa, estadoConservacion, codigoRegion, activo) "
            f"VALUES ({sql_str(cod)}, {sql_str(nombre)}, {sql_str(f_creacion)}, {sup}, {sql_str(ubicacion)}, {pres}, {cap}, {sql_str(estado)}, {sql_str(cod_reg)}, TRUE);"
        )
    lines.append("")

    # 3. SECTORES MARINOS (35 a 60 -> 3 por centro = 45 sectores)
    niveles_acceso = ["Público", "Restringido", "Solo Investigación"]
    sectores = []  # (codigoCentro, numeroInterno)
    lines.append("-- 3. SECTOR_MARINO")
    for cod_cen in centros:
        for num in range(1, 4):
            nombre = f"Sector {random.choice(['Arrecife', 'Bahía', 'Fosa', 'Canal', 'Islote', 'Estuario'])} {num} ({cod_cen})"
            ext = round(random.uniform(25.0, 1200.0), 2)
            prof = round(random.uniform(5.0, 180.0), 2)
            temp = round(random.uniform(4.5, 22.0), 1)
            acceso = random.choice(niveles_acceso)
            biodiv = round(random.uniform(30.0, 98.5), 2)
            sectores.append((cod_cen, num))
            lines.append(
                f"INSERT INTO sector_marino (codigoCentro, numeroInterno, nombre, extension, profundidadPromedio, temperatura, nivelAcceso, biodiversidadEstimada) "
                f"VALUES ({sql_str(cod_cen)}, {num}, {sql_str(nombre)}, {ext}, {prof}, {temp}, {sql_str(acceso)}, {biodiv});"
            )
    lines.append("")

    # 4, 5, 6, 7. ESPECIES MARINAS Y SUBTIPOS (60 a 120 -> generamos 80)
    estados_especie = [
        "Preocupación Menor",
        "Casi Amenazada",
        "Vulnerable",
        "En Peligro",
        "En Peligro Crítico",
    ]
    especies = []
    lines.append("-- 4. ESPECIE_MARINA Y SUBTIPOS (PEZ, MAMIFERO_MARINO, CORAL)")
    for idx in range(1, 81):
        cod = f"ESP-{idx:03d}"
        cientifico = f"{fake.last_name()}us {fake.word().lower()}is_{idx}"
        comun = f"Especie Marina {fake.word().capitalize()} {idx}"
        estado = random.choice(estados_especie)
        f_inc = fake.date_between(start_date="-8y", end_date="today")
        dist = random.choice(["Zona Norte", "Zona Centro", "Zona Sur", "Archipiélagos", "Aguas Profundas"])
        especies.append(cod)

        lines.append(
            f"INSERT INTO especie_marina (codigoEspecie, nombreCientifico, nombreComun, estadoConservacion, fechaIncorporacion, distribucionGeografica, activo) "
            f"VALUES ({sql_str(cod)}, {sql_str(cientifico)}, {sql_str(comun)}, {sql_str(estado)}, {sql_str(f_inc)}, {sql_str(dist)}, TRUE);"
        )

        # Distribución: 30 peces, 22 mamíferos, 18 corales, 10 sin clasificar (especialización parcial)
        if idx <= 30:
            largo = round(random.uniform(12.0, 320.0), 2)
            prof_h = round(random.uniform(5.0, 400.0), 2)
            escamas = "TRUE" if random.random() > 0.15 else "FALSE"
            lines.append(
                f"INSERT INTO pez (codigoEspecie, largoPromedio, profundidadHabitat, escamas) "
                f"VALUES ({sql_str(cod)}, {largo}, {prof_h}, {escamas});"
            )
        elif idx <= 52:
            peso = round(random.uniform(45.0, 28000.0), 2)
            gest = random.randint(9, 18)
            alim = random.choice(["Krill y plancton", "Peces pelágicos", "Cefalópodos", "Omnívoro marino"])
            lines.append(
                f"INSERT INTO mamifero_marino (codigoEspecie, pesoPromedio, periodoGestacional, alimentacion) "
                f"VALUES ({sql_str(cod)}, {peso}, {gest}, {sql_str(alim)});"
            )
        elif idx <= 70:
            arrecife = random.choice(["Costero", "Barrera", "Atolón", "Profundo"])
            tasa = round(random.uniform(0.5, 12.0), 2)
            luz = "TRUE" if arrecife != "Profundo" else "FALSE"
            lines.append(
                f"INSERT INTO coral (codigoEspecie, tipoArrecife, tasaCrecimiento, requiereLuz) "
                f"VALUES ({sql_str(cod)}, {sql_str(arrecife)}, {tasa}, {luz});"
            )
    lines.append("")

    # 8. MONITOREOS DE ESPECIES (250 a 500 -> generamos 360)
    lines.append("-- 8. MONITOREO_ESPECIE")
    for idx in range(1, 361):
        cod_cen, num_sec = random.choice(sectores)
        cod_esp = random.choice(especies)
        f_mon = fake.date_between(start_date=date(2025, 1, 1), end_date=date(2026, 11, 15))
        cant = random.randint(1, 140)
        cond = random.choice([
            "Oleaje moderado, visibilidad alta",
            "Corriente fría, cielo despejado",
            "Marea baja, agua turbia",
            "Condiciones estables, baja salinidad",
        ])
        obs = f"Avistamiento registrado en transecto #{random.randint(1, 10)}" if random.random() > 0.25 else None
        lines.append(
            f"INSERT INTO monitoreo_especie (codigoCentro, numeroInterno, codigoEspecie, fecha, cantidadObservada, condicionesAmbientales, observaciones) "
            f"VALUES ({sql_str(cod_cen)}, {num_sec}, {sql_str(cod_esp)}, {sql_str(f_mon)}, {cant}, {sql_str(cond)}, {sql_str(obs)});"
        )
    lines.append("")

    # 9. VISITANTES (150 a 300 -> generamos 200)
    visitantes = list(range(1, 201))
    lines.append("-- 9. VISITANTE")
    for vid in visitantes:
        nombres = f"{fake.first_name()} {fake.first_name()}"
        ap_p = fake.last_name()
        ap_m = fake.last_name()
        tel = f"+569{random.randint(10000000, 99999999)}"
        correo = f"visitante.{vid}.{ap_p.lower()}@correo.cl".replace(" ", "")
        lines.append(
            f"INSERT INTO visitante (idVisitante, nombres, apellidoP, apellidoM, telefono, correoPersonal) "
            f"VALUES ({vid}, {sql_str(nombres)}, {sql_str(ap_p)}, {sql_str(ap_m)}, {sql_str(tel)}, {sql_str(correo)});"
        )
    lines.append("")

    # 10. ACTIVIDADES (120 a 250 -> generamos 160)
    tipos_act = [
        "Actividad Educativa",
        "Recorrido Guiado",
        "Programa de Observación Marina",
        "Voluntariado Costero",
    ]
    actividades = []  # (idActividad, fechaProgramada, cupoMaximo)
    lines.append("-- 10. ACTIVIDAD")
    for aid in range(1, 161):
        cod_cen, num_sec = random.choice(sectores)
        tipo = random.choice(tipos_act)
        f_prog = fake.date_between(start_date=date(2025, 6, 1), end_date=date(2026, 12, 20))
        hora = f"{random.randint(8, 16):02d}:00:00"
        cupo = random.randint(15, 45)
        actividades.append((aid, f_prog, cupo))
        lines.append(
            f"INSERT INTO actividad (idActividad, codigoCentro, numeroInterno, tipoActividad, fechaProgramada, horaInicio, cupoMaximo) "
            f"VALUES ({aid}, {sql_str(cod_cen)}, {num_sec}, {sql_str(tipo)}, {sql_str(f_prog)}, {sql_str(hora)}, {cupo});"
        )
    lines.append("")

    # 11. PARTICIPACIONES / RESERVAS (800 a 1500 -> generamos ~1100 sin duplicar PK)
    participaciones = []  # (idVisitante, idActividad, fechaProgramada, asistencia)
    pares_usados = set()
    lines.append("-- 11. PARTICIPACION")
    for aid, f_prog, cupo in actividades:
        n_inscritos = random.randint(4, min(cupo, 14))
        elegidos = random.sample(visitantes, n_inscritos)
        for vid in elegidos:
            if (vid, aid) in pares_usados:
                continue
            pares_usados.add((vid, aid))
            f_reg = datetime.combine(f_prog - timedelta(days=random.randint(1, 15)), time(random.randint(9, 20), 0))
            asistio = random.random() < 0.78  # ~78% de asistencia efectiva
            participaciones.append((vid, aid, f_prog, asistio))
            lines.append(
                f"INSERT INTO participacion (idVisitante, idActividad, fechaRegistro, asistencia) "
                f"VALUES ({vid}, {aid}, {sql_str(f_reg.strftime('%Y-%m-%d %H:%M:%S'))}, {'TRUE' if asistio else 'FALSE'});"
            )
    lines.append("")

    # 12. EVALUACIONES (400 a 900 -> generamos ~600 sobre participaciones con asistencia efectiva)
    asistentes_efectivos = [p for p in participaciones if p[3]]
    muestra_eval = random.sample(asistentes_efectivos, min(620, len(asistentes_efectivos)))
    correlativo_por_act = {}
    lines.append("-- 12. EVALUACION")
    for vid, aid, f_prog, _ in muestra_eval:
        correlativo_por_act[aid] = correlativo_por_act.get(aid, 0) + 1
        corr = correlativo_por_act[aid]
        nota = round(random.uniform(3.5, 7.0), 1)
        f_eva = f_prog + timedelta(days=random.randint(0, 5))
        coment = random.choice([
            "Excelente guía y contenido educativo.",
            "Muy buena experiencia de avistamiento.",
            "Buena organización, aunque el clima estuvo frío.",
            "Aprendimos mucho sobre conservación marina.",
            None,
        ])
        lines.append(
            f"INSERT INTO evaluacion (idActividad, numeroCorrelativo, idVisitante, calificacion, fecha, comentario) "
            f"VALUES ({aid}, {corr}, {vid}, {nota}, {sql_str(f_eva)}, {sql_str(coment)});"
        )
    lines.append("")

    # 13. TRABAJADORES (40 a 80 -> generamos 50, con supervisores)
    cargos = ["Administrador", "Guardaparques Marino", "Conservacionista", "Investigador"]
    trabajadores = []
    lines.append("-- 13. TRABAJADOR")
    for idx in range(1, 51):
        rut = f"{15000000 + idx * 13579}-{idx % 9}"
        nombre = f"{fake.first_name()} {fake.last_name()} {fake.last_name()}"
        f_cont = fake.date_between(start_date="-10y", end_date="-2m")
        cargo = cargos[0] if idx <= 5 else random.choice(cargos[1:])
        supervisor = "NULL" if idx <= 5 else sql_str(trabajadores[random.randint(0, 4)])
        trabajadores.append(rut)
        lines.append(
            f"INSERT INTO trabajador (rutTrabajador, nombreCompleto, fechaContratacion, cargo, rutSupervisor) "
            f"VALUES ({sql_str(rut)}, {sql_str(nombre)}, {sql_str(f_cont)}, {sql_str(cargo)}, {supervisor});"
        )
    lines.append("")

    # 14, 15, 16, 17. ROLES, PERMISOS, CUENTAS DE USUARIO (40 a 80 -> 45 cuentas)
    lines.append("-- 14, 15, 16, 17. ROL, ROL_PERMISO, CUENTA_USUARIO, USUARIO_ROL")
    lines.append("INSERT INTO rol (idRol, nombreRol, descripcion) VALUES (1, 'Administrador', 'Acceso total a CRUD, reservas y gestión de usuarios');")
    lines.append("INSERT INTO rol (idRol, nombreRol, descripcion) VALUES (2, 'Operador', 'Registro de reservas y consulta de dashboard');")
    lines.append("INSERT INTO rol (idRol, nombreRol, descripcion) VALUES (3, 'Investigador', 'Consulta de dashboard y gestión de especies');")

    permisos_map = {
        1: ["VER_DASHBOARD", "CREAR_RESERVA", "CRUD_CENTROS", "CRUD_ESPECIES", "GESTION_USUARIOS"],
        2: ["VER_DASHBOARD", "CREAR_RESERVA"],
        3: ["VER_DASHBOARD", "CRUD_ESPECIES"],
    }
    for id_rol, perms in permisos_map.items():
        for p in perms:
            lines.append(f"INSERT INTO rol_permiso (idRol, permiso) VALUES ({id_rol}, {sql_str(p)});")

    # Cuentas de prueba conocidas para la defensa + 42 cuentas sintéticas
    cuentas_demo = [
        (1, trabajadores[0], "admin", "admin123", 1),
        (2, trabajadores[5], "operador", "oper123", 2),
        (3, trabajadores[6], "investigador", "inv123", 3),
    ]
    for cid, rut, user, pwd, id_rol in cuentas_demo:
        lines.append(
            f"INSERT INTO cuenta_usuario (idCuenta, rutTrabajador, fechaCreacion, nombreUsuario, passwordHash, activa) "
            f"VALUES ({cid}, {sql_str(rut)}, '2026-01-10', {sql_str(user)}, {sql_str(pwd)}, TRUE);"
        )
        lines.append(f"INSERT INTO usuario_rol (idCuenta, idRol) VALUES ({cid}, {id_rol});")

    for idx in range(4, 46):
        rut = trabajadores[idx - 1]
        uname = f"user_{idx:02d}"
        id_rol = random.choice([1, 2, 3])
        lines.append(
            f"INSERT INTO cuenta_usuario (idCuenta, rutTrabajador, fechaCreacion, nombreUsuario, passwordHash, activa) "
            f"VALUES ({idx}, {sql_str(rut)}, '2026-03-01', {sql_str(uname)}, 'clave2026', TRUE);"
        )
        lines.append(f"INSERT INTO usuario_rol (idCuenta, idRol) VALUES ({idx}, {id_rol});")

    lines.append("")
    lines.append("SET FOREIGN_KEY_CHECKS = 1;")

    with open(OUTPUT_SQL, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Archivo generado exitosamente: {OUTPUT_SQL}")
    print(f"Total participaciones: {len(participaciones)} | Total evaluaciones: {len(muestra_eval)}")


if __name__ == "__main__":
    main()