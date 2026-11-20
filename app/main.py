import datetime
import pandas as pd
import plotly.express as px
import streamlit as st
from app import negocio

st.set_page_config(
    page_title="Conservación Marina - Caso 3 (Grupo 3)",
    page_icon="🌊",
    layout="wide",
)

# ============================================================================
# GESTIÓN DE SESIÓN Y LOGIN (Funcionalidad 3: Control de Usuarios y Roles)
# ============================================================================
if "usuario" not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    st.title("🌊 Sistema Integral de Gestión de Centros de Conservación Marina")
    st.subheader("Acceso al Producto Mínimo Viable (Caso 3 — Grupo 3)")

    col1, col2 = st.columns([1, 1])
    with col1:
        with st.form("form_login"):
            user_input = st.text_input("Nombre de usuario")
            pass_input = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("Iniciar sesión")

            if submitted:
                user_data = negocio.autenticar_usuario(user_input, pass_input)
                if user_data:
                    st.session_state.usuario = user_data
                    st.rerun()
                else:
                    st.error("Credenciales inválidas o cuenta inactiva.")

    with col2:
        st.info(
            "**Cuentas de prueba disponibles (poblamiento sintético):**\n\n"
            "- **Administrador:** `admin` / `admin123` (Acceso total)\n"
            "- **Operador:** `operador` / `oper123` (Reservas y Dashboard)\n"
            "- **Investigador:** `investigador` / `inv123` (CRUD Especies y Dashboard)"
        )
    st.stop()

# ============================================================================
# BARRA LATERAL Y PERMISOS REALES POR ROL
# ============================================================================
usuario = st.session_state.usuario
permisos = set(usuario["permisos"])

with st.sidebar:
    st.header("👤 Sesión Activa")
    st.write(f"**Trabajador:** {usuario['nombreCompleto']}")
    st.write(f"**Cargo:** {usuario['cargo']}")
    st.write(f"**Rol:** `{usuario['nombreRol']}`")
    st.caption(f"Permisos activos: {', '.join(sorted(permisos))}")

    if st.button("Cerrar sesión"):
        st.session_state.usuario = None
        st.rerun()

    st.divider()
    opciones_menu = []
    if "VER_DASHBOARD" in permisos:
        opciones_menu.append("📊 Dashboard Analítico")
    if "CREAR_RESERVA" in permisos:
        opciones_menu.append("📝 Formulario de Reservas")
    if "CRUD_CENTROS" in permisos or "CRUD_ESPECIES" in permisos:
        opciones_menu.append("🗂️ CRUD Tablas Maestras")

    if not opciones_menu:
        st.warning("Tu rol no tiene módulos habilitados.")
        st.stop()

    seccion = st.radio("Módulos habilitados:", opciones_menu)

st.title("🌊 Gestión de Centros de Conservación Marina")

# ============================================================================
# MÓDULO 4: DASHBOARD (3 Preguntas Fase 1 + 4ª Pregunta Propuesta)
# ============================================================================
if seccion == "📊 Dashboard Analítico":
    st.header("📊 Panel de Información y Toma de Decisiones")

    centros = negocio.listar_centros()
    mapa_centros = {"TODOS": "Todos los Centros"} | {
        c["codigoCentro"]: f"{c['codigoCentro']} - {c['nombre']}" for c in centros
    }

    regiones = negocio.listar_regiones()
    mapa_regiones = {"TODAS": "Todas las Regiones Marítimas"} | {
        r["codigoRegion"]: r["nombreOficial"] for r in regiones
    }

    # --- PREGUNTA 1 FASE 1 ---
    st.subheader("1. Sectores que concentran mayor cantidad de actividades y visitantes")
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        sel_centro_q1 = st.selectbox(
            "Filtrar por Centro:",
            options=list(mapa_centros.keys()),
            format_func=lambda k: mapa_centros[k],
            key="q1_centro",
        )
    with f_col2:
        f_ini = st.date_input("Fecha inicio:", value=datetime.date(2025, 6, 1))
    with f_col3:
        f_fin = st.date_input("Fecha término:", value=datetime.date(2026, 12, 31))

    data_q1 = negocio.dash_q1_sectores_actividad(sel_centro_q1, str(f_ini), str(f_fin))
    if data_q1:
        df_q1 = pd.DataFrame(data_q1)
        fig1 = px.bar(
            df_q1,
            x="sector",
            y=["visitantes", "actividades"],
            barmode="group",
            title="Ranking de Visitantes y Actividades por Sector Marino",
            labels={"value": "Cantidad", "sector": "Sector Marino", "variable": "Métrica"},
        )
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("No hay actividades registradas para los filtros seleccionados.")

    st.divider()

    # --- PREGUNTA 2 Y 3 FASE 1 ---
    col_q2, col_q3 = st.columns(2)

    with col_q2:
        st.subheader("2. Distribución de especies monitoreadas por clasificación")
        sel_centro_q2 = st.selectbox(
            "Filtrar por Centro:",
            options=list(mapa_centros.keys()),
            format_func=lambda k: mapa_centros[k],
            key="q2_centro",
        )
        data_q2 = negocio.dash_q2_distribucion_especies(sel_centro_q2)
        if data_q2:
            df_q2 = pd.DataFrame(data_q2)
            fig2 = px.pie(
                df_q2,
                names="tipo",
                values="ejemplaresObservados",
                hole=0.4,
                title="Composición de Ejemplares Observados (Pez, Mamífero, Coral)",
            )
            st.plotly_chart(fig2, use_container_width=True)
            st.dataframe(df_q2, use_container_width=True, hide_index=True)

    with col_q3:
        st.subheader("3. Relación entre participantes por actividad y evaluación promedio")
        sel_centro_q3 = st.selectbox(
            "Filtrar por Centro:",
            options=list(mapa_centros.keys()),
            format_func=lambda k: mapa_centros[k],
            key="q3_centro",
        )
        data_q3 = negocio.dash_q3_participantes_evaluacion(sel_centro_q3)
        if data_q3:
            df_q3 = pd.DataFrame(data_q3)
            fig3 = px.scatter(
                df_q3,
                x="participantes",
                y="evaluacionPromedio",
                color="tipoActividad",
                hover_data=["centro", "sector", "idActividad"],
                title="Participantes vs. Calificación Promedio por Actividad",
                labels={
                    "participantes": "Cantidad de Participantes",
                    "evaluacionPromedio": "Nota Promedio (1.0 - 7.0)",
                },
            )
            st.plotly_chart(fig3, use_container_width=True)
            st.dataframe(df_q3.head(10), use_container_width=True, hide_index=True)

    st.divider()

    # --- PREGUNTA 4 PROPUESTA POR EL EQUIPO ---
    st.subheader("4. [Pregunta Propuesta] Evolución mensual de monitoreos según estado de conservación")
    st.caption(
        "**Justificación de negocio:** Permite evaluar si las especies en categorías críticas "
        "('En Peligro', 'En Peligro Crítico', 'Vulnerable') mantienen cobertura constante de avistamientos "
        "por región marítima para priorizar presupuesto y patrullaje."
    )
    sel_region_q4 = st.selectbox(
        "Filtrar por Región Marítima:",
        options=list(mapa_regiones.keys()),
        format_func=lambda k: mapa_regiones[k],
        key="q4_region",
    )
    data_q4 = negocio.dash_q4_monitoreo_estado_conservacion(sel_region_q4)
    if data_q4:
        df_q4 = pd.DataFrame(data_q4)
        fig4 = px.line(
            df_q4,
            x="mes",
            y="totalObservados",
            color="estadoConservacion",
            markers=True,
            title="Tendencia Mensual de Ejemplares Observados por Estado de Conservación",
            labels={"mes": "Mes", "totalObservados": "Total Ejemplares", "estadoConservacion": "Estado UICN"},
        )
        st.plotly_chart(fig4, use_container_width=True)

# ============================================================================
# MÓDULO 1: FORMULARIO TRANSACCIONAL (Reserva / Participación)
# ============================================================================
elif seccion == "📝 Formulario de Reservas":
    if "CREAR_RESERVA" not in permisos:
        st.error("Acceso denegado: tu rol no posee permiso CREAR_RESERVA.")
        st.stop()

    st.header("📝 Registro Transaccional de Participación / Reserva")
    visitantes = negocio.listar_visitantes()
    actividades = negocio.listar_actividades_disponibles()

    if not visitantes or not actividades:
        st.warning("Faltan visitantes o actividades activas en la base de datos.")
        st.stop()

    map_vis = {v["idVisitante"]: v["etiqueta"] for v in visitantes}
    map_act = {
        a["idActividad"]: f"{a['etiqueta']} — Cupos: {a['inscritosActuales']}/{a['cupoMaximo']}"
        for a in actividades
    }

    with st.form("form_reserva"):
        vis_id = st.selectbox("Seleccione Visitante:", list(map_vis.keys()), format_func=lambda x: map_vis[x])
        act_id = st.selectbox("Seleccione Actividad Marina:", list(map_act.keys()), format_func=lambda x: map_act[x])
        asistencia = st.checkbox("Confirmar asistencia efectiva inmediata", value=False)
        enviar = st.form_submit_button("Registrar Participación")

        if enviar:
            ok, msg = negocio.registrar_participacion_transaccional(vis_id, act_id, asistencia)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

# ============================================================================
# MÓDULO 2: CRUD DE TABLAS MAESTRAS (Centros y Especies)
# ============================================================================
elif seccion == "🗂️ CRUD Tablas Maestras":
    st.header("🗂️ Administración de Tablas Maestras")
    tabs = []
    if "CRUD_CENTROS" in permisos:
        tabs.append("🏛️ Centros de Conservación")
    if "CRUD_ESPECIES" in permisos:
        tabs.append("🐋 Especies Marinas")

    tab_objs = st.tabs(tabs)
    idx_tab = 0

    # --- CRUD 1: CENTRO_CONSERVACION ---
    if "CRUD_CENTROS" in permisos:
        with tab_objs[idx_tab]:
            idx_tab += 1
            st.subheader("Gestión de Centros de Conservación")
            centros = negocio.listar_centros()
            st.dataframe(pd.DataFrame(centros), use_container_width=True, hide_index=True)

            col_c1, col_c2 = st.columns(2)
            with col_c1:
                st.markdown("**➕ Crear Nuevo Centro**")
                regiones = negocio.listar_regiones()
                map_reg = {r["codigoRegion"]: r["nombreOficial"] for r in regiones}
                with st.form("crear_centro"):
                    cod = st.text_input("Código Centro (ej. CEN-020)")
                    nom = st.text_input("Nombre del Centro")
                    f_crea = st.date_input("Fecha Creación", value=datetime.date.today())
                    sup = st.number_input("Superficie Protegida (ha)", min_value=1.0, value=1200.0)
                    ubi = st.text_input("Ubicación")
                    pres = st.number_input("Presupuesto Anual ($)", min_value=0.0, value=25000000.0)
                    cap = st.number_input("Capacidad Operativa", min_value=1, value=80)
                    est = st.selectbox("Estado Conservación", ["Óptimo", "Estable", "En Recuperación", "Crítico"])
                    reg = st.selectbox("Región Marítima", list(map_reg.keys()), format_func=lambda x: map_reg[x])
                    if st.form_submit_button("Guardar Centro"):
                        if not cod.strip() or not nom.strip() or not ubi.strip():
                            st.error("Código, nombre y ubicación son obligatorios.")
                        else:
                            ok, msg = negocio.crear_centro({
                                "codigo": cod.strip(),
                                "nombre": nom.strip(),
                                "fecha": str(f_crea),
                                "superficie": sup,
                                "ubicacion": ubi.strip(),
                                "presupuesto": pres,
                                "capacidad": cap,
                                "estado": est,
                                "region": reg,
                            })
                            st.success(msg) if ok else st.error(msg)

            with col_c2:
                st.markdown("**✏️ Modificar / Desactivar Lógicamente Centro**")
                if centros:
                    cods_c = [c["codigoCentro"] for c in centros]
                    sel_c = st.selectbox("Seleccionar Centro:", cods_c, key="edit_centro_sel")
                    actual_c = next(c for c in centros if c["codigoCentro"] == sel_c)

                    with st.form("editar_centro"):
                        e_nom = st.text_input("Nombre", value=actual_c["nombre"])
                        e_ubi = st.text_input("Ubicación", value=actual_c["ubicacion"])
                        e_pres = st.number_input("Presupuesto", min_value=0.0, value=float(actual_c["presupuesto"]))
                        e_cap = st.number_input("Capacidad", min_value=1, value=int(actual_c["capacidadOperativa"]))
                        estados_c = ["Óptimo", "Estable", "En Recuperación", "Crítico"]
                        e_est = st.selectbox("Estado", estados_c, index=estados_c.index(actual_c["estadoConservacion"]))
                        if st.form_submit_button("Actualizar Datos"):
                            ok, msg = negocio.actualizar_centro({
                                "codigo": sel_c,
                                "nombre": e_nom.strip(),
                                "ubicacion": e_ubi.strip(),
                                "presupuesto": e_pres,
                                "capacidad": e_cap,
                                "estado": e_est,
                            })
                            st.success(msg) if ok else st.error(msg)

                    nuevo_estado = not bool(actual_c["activo"])
                    label_btn = "Reactivar Centro" if nuevo_estado else "Desactivar Centro (Borrado Lógico)"
                    if st.button(label_btn, key="toggle_centro"):
                        ok, msg = negocio.cambiar_estado_centro(sel_c, nuevo_estado)
                        st.success(msg) if ok else st.error(msg)

    # --- CRUD 2: ESPECIE_MARINA ---
    if "CRUD_ESPECIES" in permisos:
        with tab_objs[idx_tab]:
            st.subheader("Gestión de Especies Marinas")
            especies = negocio.listar_especies()
            st.dataframe(pd.DataFrame(especies), use_container_width=True, hide_index=True)

            col_e1, col_e2 = st.columns(2)
            with col_e1:
                st.markdown("**➕ Registrar Nueva Especie**")
                estados_e = ["Preocupación Menor", "Casi Amenazada", "Vulnerable", "En Peligro", "En Peligro Crítico"]
                with st.form("crear_especie"):
                    e_cod = st.text_input("Código Especie (ej. ESP-099)")
                    e_cie = st.text_input("Nombre Científico")
                    e_com = st.text_input("Nombre Común")
                    e_est = st.selectbox("Estado Conservación", estados_e)
                    e_fec = st.date_input("Fecha Incorporación", value=datetime.date.today())
                    e_dis = st.text_input("Distribución Geográfica", value="Zona Centro")
                    if st.form_submit_button("Guardar Especie"):
                        if not e_cod.strip() or not e_cie.strip() or not e_com.strip():
                            st.error("Código, nombre científico y nombre común son obligatorios.")
                        else:
                            ok, msg = negocio.crear_especie({
                                "codigo": e_cod.strip(),
                                "cientifico": e_cie.strip(),
                                "comun": e_com.strip(),
                                "estado": e_est,
                                "fecha": str(e_fec),
                                "distribucion": e_dis.strip(),
                            })
                            st.success(msg) if ok else st.error(msg)

            with col_e2:
                st.markdown("**✏️ Modificar / Desactivar Lógicamente Especie**")
                if especies:
                    cods_e = [e["codigoEspecie"] for e in especies]
                    sel_e = st.selectbox("Seleccionar Especie:", cods_e, key="edit_especie_sel")
                    actual_e = next(e for e in especies if e["codigoEspecie"] == sel_e)
                    estados_e = ["Preocupación Menor", "Casi Amenazada", "Vulnerable", "En Peligro", "En Peligro Crítico"]

                    with st.form("editar_especie"):
                        u_com = st.text_input("Nombre Común", value=actual_e["nombreComun"])
                        u_est = st.selectbox("Estado", estados_e, index=estados_e.index(actual_e["estadoConservacion"]))
                        u_dis = st.text_input("Distribución", value=actual_e["distribucionGeografica"])
                        if st.form_submit_button("Actualizar Especie"):
                            ok, msg = negocio.actualizar_especie({
                                "codigo": sel_e,
                                "comun": u_com.strip(),
                                "estado": u_est,
                                "distribucion": u_dis.strip(),
                            })
                            st.success(msg) if ok else st.error(msg)

                    nuevo_est_e = not bool(actual_e["activo"])
                    label_btn_e = "Reactivar Especie" if nuevo_est_e else "Desactivar Especie (Borrado Lógico)"
                    if st.button(label_btn_e, key="toggle_especie"):
                        ok, msg = negocio.cambiar_estado_especie(sel_e, nuevo_est_e)
                        st.success(msg) if ok else st.error(msg)
                    