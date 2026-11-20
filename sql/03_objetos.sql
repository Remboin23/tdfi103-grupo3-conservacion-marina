-- ============================================================================
-- PROYECTO SEMESTRAL 2026 - TDFI103 BASES DE DATOS (UNAB)
-- GRUPO 3 - CASO 3: Sistema Integral de Gestión de Centros de Conservación Marina
-- Archivo: sql/02_objetos.sql (6 Vistas y 6 Procedimientos Almacenados)
-- ============================================================================

USE conservacion_marina;

-- ============================================================================
-- 6 VISTAS OBLIGATORIAS (R2, R3, R5, R6, R7, R8)
-- ============================================================================

-- R2: Distribución de especies clasificadas entre peces, mamíferos marinos y corales,
-- considerando el centro y sector donde han sido monitoreadas.
CREATE OR REPLACE VIEW v_r2_distribucion_especies_sector AS
SELECT
    c.codigoCentro,
    c.nombre AS nombreCentro,
    s.numeroInterno AS numeroSector,
    s.nombre AS nombreSector,
    CASE
        WHEN p.codigoEspecie IS NOT NULL THEN 'Pez'
        WHEN mm.codigoEspecie IS NOT NULL THEN 'Mamífero Marino'
        WHEN co.codigoEspecie IS NOT NULL THEN 'Coral'
        ELSE 'No Clasificada'
    END AS clasificacionEspecie,
    COUNT(DISTINCT e.codigoEspecie) AS cantidadEspeciesDistintas,
    SUM(m.cantidadObservada) AS totalEjemplaresObservados
FROM centro_conservacion c
JOIN sector_marino s
    ON c.codigoCentro = s.codigoCentro
JOIN monitoreo_especie m
    ON s.codigoCentro = m.codigoCentro AND s.numeroInterno = m.numeroInterno
JOIN especie_marina e
    ON m.codigoEspecie = e.codigoEspecie
LEFT JOIN pez p
    ON e.codigoEspecie = p.codigoEspecie
LEFT JOIN mamifero_marino mm
    ON e.codigoEspecie = mm.codigoEspecie
LEFT JOIN coral co
    ON e.codigoEspecie = co.codigoEspecie
GROUP BY
    c.codigoCentro, c.nombre, s.numeroInterno, s.nombre, clasificacionEspecie
ORDER BY
    c.codigoCentro, s.numeroInterno, clasificacionEspecie;


-- R3: Relación entre cantidad de participantes de una actividad y su evaluación promedio,
-- considerando además el centro y sector donde se realiza.
CREATE OR REPLACE VIEW v_r3_participantes_vs_evaluacion AS
SELECT
    c.codigoCentro,
    c.nombre AS nombreCentro,
    s.numeroInterno AS numeroSector,
    s.nombre AS nombreSector,
    a.idActividad,
    a.tipoActividad,
    a.fechaProgramada,
    COUNT(DISTINCT p.idVisitante) AS cantidadParticipantes,
    COUNT(DISTINCT ev.numeroCorrelativo) AS cantidadEvaluaciones,
    ROUND(AVG(ev.calificacion), 2) AS promedioEvaluacion
FROM centro_conservacion c
JOIN sector_marino s
    ON c.codigoCentro = s.codigoCentro
JOIN actividad a
    ON s.codigoCentro = a.codigoCentro AND s.numeroInterno = a.numeroInterno
LEFT JOIN participacion p
    ON a.idActividad = p.idActividad
LEFT JOIN evaluacion ev
    ON a.idActividad = ev.idActividad
GROUP BY
    c.codigoCentro, c.nombre, s.numeroInterno, s.nombre,
    a.idActividad, a.tipoActividad, a.fechaProgramada
ORDER BY
    cantidadParticipantes DESC, promedioEvaluacion DESC;


-- R5: Sectores con mayor tasa de asistencia efectiva respecto del total de participaciones registradas.
CREATE OR REPLACE VIEW v_r5_tasa_asistencia_sector AS
SELECT
    c.codigoCentro,
    c.nombre AS nombreCentro,
    s.numeroInterno AS numeroSector,
    s.nombre AS nombreSector,
    COUNT(p.idVisitante) AS totalReservas,
    SUM(CASE WHEN p.asistencia = TRUE THEN 1 ELSE 0 END) AS asistenciasEfectivas,
    ROUND(
        (SUM(CASE WHEN p.asistencia = TRUE THEN 1 ELSE 0 END) / COUNT(p.idVisitante)) * 100,
        2
    ) AS tasaAsistenciaPorcentaje
FROM centro_conservacion c
JOIN sector_marino s
    ON c.codigoCentro = s.codigoCentro
JOIN actividad a
    ON s.codigoCentro = a.codigoCentro AND s.numeroInterno = a.numeroInterno
JOIN participacion p
    ON a.idActividad = p.idActividad
GROUP BY
    c.codigoCentro, c.nombre, s.numeroInterno, s.nombre
ORDER BY
    tasaAsistenciaPorcentaje DESC, totalReservas DESC;


-- R6: Especies con mayor cantidad observada acumulada por centro y sector durante los monitoreos.
CREATE OR REPLACE VIEW v_r6_especies_acumuladas_sector AS
SELECT
    c.codigoCentro,
    c.nombre AS nombreCentro,
    s.numeroInterno AS numeroSector,
    s.nombre AS nombreSector,
    e.codigoEspecie,
    e.nombreComun,
    e.nombreCientifico,
    COUNT(m.idMonitoreo) AS totalMonitoreos,
    SUM(m.cantidadObservada) AS cantidadObservadaAcumulada
FROM centro_conservacion c
JOIN sector_marino s
    ON c.codigoCentro = s.codigoCentro
JOIN monitoreo_especie m
    ON s.codigoCentro = m.codigoCentro AND s.numeroInterno = m.numeroInterno
JOIN especie_marina e
    ON m.codigoEspecie = e.codigoEspecie
GROUP BY
    c.codigoCentro, c.nombre, s.numeroInterno, s.nombre,
    e.codigoEspecie, e.nombreComun, e.nombreCientifico
ORDER BY
    cantidadObservadaAcumulada DESC;


-- R7: Centros con mayor diversidad de especies monitoreadas y distribución de sus estados de conservación.
CREATE OR REPLACE VIEW v_r7_diversidad_estado_centro AS
SELECT
    c.codigoCentro,
    c.nombre AS nombreCentro,
    e.estadoConservacion,
    COUNT(DISTINCT e.codigoEspecie) AS especiesDistintasMonitoreadas,
    COUNT(m.idMonitoreo) AS totalRegistrosMonitoreo,
    SUM(m.cantidadObservada) AS ejemplaresTotales
FROM centro_conservacion c
JOIN sector_marino s
    ON c.codigoCentro = s.codigoCentro
JOIN monitoreo_especie m
    ON s.codigoCentro = m.codigoCentro AND s.numeroInterno = m.numeroInterno
JOIN especie_marina e
    ON m.codigoEspecie = e.codigoEspecie
GROUP BY
    c.codigoCentro, c.nombre, e.estadoConservacion
ORDER BY
    especiesDistintasMonitoreadas DESC, c.codigoCentro;


-- R8: Visitantes con mayor participación en actividades y su evaluación promedio (con HAVING).
CREATE OR REPLACE VIEW v_r8_visitantes_participacion_evaluacion AS
SELECT
    v.idVisitante,
    CONCAT(v.nombres, ' ', v.apellidoP, ' ', v.apellidoM) AS nombreCompleto,
    v.correoPersonal,
    COUNT(DISTINCT p.idActividad) AS actividadesInscritas,
    SUM(CASE WHEN p.asistencia = TRUE THEN 1 ELSE 0 END) AS asistenciasEfectivas,
    COUNT(ev.numeroCorrelativo) AS evaluacionesRealizadas,
    ROUND(AVG(ev.calificacion), 2) AS evaluacionPromedio
FROM visitante v
JOIN participacion p
    ON v.idVisitante = p.idVisitante
JOIN actividad a
    ON p.idActividad = a.idActividad
LEFT JOIN evaluacion ev
    ON p.idVisitante = ev.idVisitante AND p.idActividad = ev.idActividad
GROUP BY
    v.idVisitante, v.nombres, v.apellidoP, v.apellidoM, v.correoPersonal
HAVING
    COUNT(DISTINCT p.idActividad) >= 2
ORDER BY
    actividadesInscritas DESC, evaluacionPromedio DESC;


-- ============================================================================
-- 6 PROCEDIMIENTOS ALMACENADOS OBLIGATORIOS (R1, R4, R9, R10, R11, R12)
-- ============================================================================

DELIMITER $$

-- R1: Sectores que concentran la mayor cantidad de actividades y visitantes durante un período.
DROP PROCEDURE IF EXISTS sp_r1_sectores_mayor_actividad$$
CREATE PROCEDURE sp_r1_sectores_mayor_actividad(
    IN p_fechaInicio DATE,
    IN p_fechaTermino DATE
)
BEGIN
    SELECT
        c.codigoCentro,
        c.nombre AS nombreCentro,
        s.numeroInterno AS numeroSector,
        s.nombre AS nombreSector,
        COUNT(DISTINCT a.idActividad) AS totalActividades,
        COUNT(p.idVisitante) AS totalParticipaciones,
        COUNT(DISTINCT p.idVisitante) AS visitantesUnicos
    FROM centro_conservacion c
    JOIN sector_marino s
        ON c.codigoCentro = s.codigoCentro
    JOIN actividad a
        ON s.codigoCentro = a.codigoCentro AND s.numeroInterno = a.numeroInterno
    LEFT JOIN participacion p
        ON a.idActividad = p.idActividad
    WHERE a.fechaProgramada BETWEEN p_fechaInicio AND p_fechaTermino
    GROUP BY
        c.codigoCentro, c.nombre, s.numeroInterno, s.nombre
    ORDER BY
        totalActividades DESC, totalParticipaciones DESC;
END$$


-- R4: Centros que concentran la mayor cantidad de actividades y visitantes durante un período.
DROP PROCEDURE IF EXISTS sp_r4_centros_mayor_actividad$$
CREATE PROCEDURE sp_r4_centros_mayor_actividad(
    IN p_fechaInicio DATE,
    IN p_fechaTermino DATE
)
BEGIN
    SELECT
        c.codigoCentro,
        c.nombre AS nombreCentro,
        c.ubicacion,
        COUNT(DISTINCT a.idActividad) AS totalActividades,
        COUNT(p.idVisitante) AS totalParticipaciones,
        COUNT(DISTINCT p.idVisitante) AS visitantesUnicos
    FROM centro_conservacion c
    JOIN sector_marino s
        ON c.codigoCentro = s.codigoCentro
    JOIN actividad a
        ON s.codigoCentro = a.codigoCentro AND s.numeroInterno = a.numeroInterno
    LEFT JOIN participacion p
        ON a.idActividad = p.idActividad
    WHERE a.fechaProgramada BETWEEN p_fechaInicio AND p_fechaTermino
    GROUP BY
        c.codigoCentro, c.nombre, c.ubicacion
    ORDER BY
        totalActividades DESC, totalParticipaciones DESC;
END$$


-- R9: Actividades que superan el promedio de participantes de las actividades realizadas
-- en el mismo centro durante un período determinado (usando subconsulta correlacionada).
DROP PROCEDURE IF EXISTS sp_r9_actividades_sobre_promedio_centro$$
CREATE PROCEDURE sp_r9_actividades_sobre_promedio_centro(
    IN p_codigoCentro VARCHAR(15),
    IN p_fechaInicio DATE,
    IN p_fechaTermino DATE
)
BEGIN
    SELECT
        c.codigoCentro,
        c.nombre AS nombreCentro,
        s.numeroInterno AS numeroSector,
        s.nombre AS nombreSector,
        a.idActividad,
        a.tipoActividad,
        a.fechaProgramada,
        COUNT(p.idVisitante) AS cantidadParticipantes
    FROM centro_conservacion c
    JOIN sector_marino s
        ON c.codigoCentro = s.codigoCentro
    JOIN actividad a
        ON s.codigoCentro = a.codigoCentro AND s.numeroInterno = a.numeroInterno
    LEFT JOIN participacion p
        ON a.idActividad = p.idActividad
    WHERE c.codigoCentro = p_codigoCentro
      AND a.fechaProgramada BETWEEN p_fechaInicio AND p_fechaTermino
    GROUP BY
        c.codigoCentro, c.nombre, s.numeroInterno, s.nombre,
        a.idActividad, a.tipoActividad, a.fechaProgramada
    HAVING COUNT(p.idVisitante) > (
        SELECT AVG(sub.conteo)
        FROM (
            SELECT COUNT(p2.idVisitante) AS conteo
            FROM actividad a2
            LEFT JOIN participacion p2 ON a2.idActividad = p2.idActividad
            WHERE a2.codigoCentro = c.codigoCentro
              AND a2.fechaProgramada BETWEEN p_fechaInicio AND p_fechaTermino
            GROUP BY a2.idActividad
        ) AS sub
    )
    ORDER BY cantidadParticipantes DESC;
END$$


-- R10: Sectores con biodiversidad estimada superior al promedio de los sectores del mismo centro
-- y qué especies se monitorean en ellos (usando subconsulta correlacionada).
DROP PROCEDURE IF EXISTS sp_r10_sectores_biodiversidad_superior$$
CREATE PROCEDURE sp_r10_sectores_biodiversidad_superior(
    IN p_codigoCentro VARCHAR(15)
)
BEGIN
    SELECT
        c.codigoCentro,
        c.nombre AS nombreCentro,
        s.numeroInterno AS numeroSector,
        s.nombre AS nombreSector,
        s.biodiversidadEstimada,
        e.codigoEspecie,
        e.nombreComun,
        e.nombreCientifico,
        SUM(m.cantidadObservada) AS totalEjemplaresMonitoreados
    FROM centro_conservacion c
    JOIN sector_marino s
        ON c.codigoCentro = s.codigoCentro
    JOIN monitoreo_especie m
        ON s.codigoCentro = m.codigoCentro AND s.numeroInterno = m.numeroInterno
    JOIN especie_marina e
        ON m.codigoEspecie = e.codigoEspecie
    WHERE c.codigoCentro = p_codigoCentro
      AND s.biodiversidadEstimada > (
          SELECT AVG(s2.biodiversidadEstimada)
          FROM sector_marino s2
          WHERE s2.codigoCentro = s.codigoCentro
      )
    GROUP BY
        c.codigoCentro, c.nombre, s.numeroInterno, s.nombre, s.biodiversidadEstimada,
        e.codigoEspecie, e.nombreComun, e.nombreCientifico
    ORDER BY
        s.biodiversidadEstimada DESC, totalEjemplaresMonitoreados DESC;
END$$


-- R11: Visitantes que han participado en más actividades que el promedio de los visitantes
-- y poseen evaluación promedio superior al promedio general durante un período.
DROP PROCEDURE IF EXISTS sp_r11_visitantes_destacados_periodo$$
CREATE PROCEDURE sp_r11_visitantes_destacados_periodo(
    IN p_fechaInicio DATE,
    IN p_fechaTermino DATE
)
BEGIN
    SELECT
        v.idVisitante,
        CONCAT(v.nombres, ' ', v.apellidoP, ' ', v.apellidoM) AS nombreCompleto,
        COUNT(DISTINCT p.idActividad) AS actividadesParticipadas,
        ROUND(AVG(ev.calificacion), 2) AS evaluacionPromedio
    FROM visitante v
    JOIN participacion p
        ON v.idVisitante = p.idVisitante
    JOIN actividad a
        ON p.idActividad = a.idActividad
    JOIN evaluacion ev
        ON p.idVisitante = ev.idVisitante AND p.idActividad = ev.idActividad
    WHERE a.fechaProgramada BETWEEN p_fechaInicio AND p_fechaTermino
    GROUP BY
        v.idVisitante, v.nombres, v.apellidoP, v.apellidoM
    HAVING
        COUNT(DISTINCT p.idActividad) > (
            SELECT AVG(t_act.cant)
            FROM (
                SELECT COUNT(DISTINCT p2.idActividad) AS cant
                FROM participacion p2
                JOIN actividad a2 ON p2.idActividad = a2.idActividad
                WHERE a2.fechaProgramada BETWEEN p_fechaInicio AND p_fechaTermino
                GROUP BY p2.idVisitante
            ) AS t_act
        )
        AND AVG(ev.calificacion) > (
            SELECT AVG(ev2.calificacion)
            FROM evaluacion ev2
            JOIN actividad a3 ON ev2.idActividad = a3.idActividad
            WHERE a3.fechaProgramada BETWEEN p_fechaInicio AND p_fechaTermino
        )
    ORDER BY
        actividadesParticipadas DESC, evaluacionPromedio DESC;
END$$


-- R12: Centros con promedio de participantes por actividad superior al promedio general
-- de los centros durante un período determinado.
DROP PROCEDURE IF EXISTS sp_r12_centros_promedio_participantes$$
CREATE PROCEDURE sp_r12_centros_promedio_participantes(
    IN p_fechaInicio DATE,
    IN p_fechaTermino DATE
)
BEGIN
    SELECT
        c.codigoCentro,
        c.nombre AS nombreCentro,
        COUNT(DISTINCT a.idActividad) AS totalActividades,
        COUNT(p.idVisitante) AS totalParticipantes,
        ROUND(COUNT(p.idVisitante) / COUNT(DISTINCT a.idActividad), 2) AS promedioParticipantesPorActividad
    FROM centro_conservacion c
    JOIN sector_marino s
        ON c.codigoCentro = s.codigoCentro
    JOIN actividad a
        ON s.codigoCentro = a.codigoCentro AND s.numeroInterno = a.numeroInterno
    LEFT JOIN participacion p
        ON a.idActividad = p.idActividad
    WHERE a.fechaProgramada BETWEEN p_fechaInicio AND p_fechaTermino
    GROUP BY
        c.codigoCentro, c.nombre
    HAVING
        (COUNT(p.idVisitante) / COUNT(DISTINCT a.idActividad)) > (
            SELECT COUNT(p2.idVisitante) / COUNT(DISTINCT a2.idActividad)
            FROM actividad a2
            LEFT JOIN participacion p2 ON a2.idActividad = p2.idActividad
            WHERE a2.fechaProgramada BETWEEN p_fechaInicio AND p_fechaTermino
        )
    ORDER BY
        promedioParticipantesPorActividad DESC;
END$$

DELIMITER ;

-- ============================================================================
-- CONSULTAS DE PRUEBA PARA CAPTURAS EN MYSQL WORKBENCH
-- ============================================================================
/*
SELECT * FROM v_r2_distribucion_especies_sector LIMIT 15;
SELECT * FROM v_r3_participantes_vs_evaluacion LIMIT 15;
SELECT * FROM v_r5_tasa_asistencia_sector LIMIT 15;
SELECT * FROM v_r6_especies_acumuladas_sector LIMIT 15;
SELECT * FROM v_r7_diversidad_estado_centro LIMIT 15;
SELECT * FROM v_r8_visitantes_participacion_evaluacion LIMIT 15;

CALL sp_r1_sectores_mayor_actividad('2025-06-01', '2026-12-31');
CALL sp_r4_centros_mayor_actividad('2025-06-01', '2026-12-31');
CALL sp_r9_actividades_sobre_promedio_centro('CEN-001', '2025-06-01', '2026-12-31');
CALL sp_r10_sectores_biodiversidad_superior('CEN-001');
CALL sp_r11_visitantes_destacados_periodo('2025-06-01', '2026-12-31');
CALL sp_r12_centros_promedio_participantes('2025-06-01', '2026-12-31');
*/