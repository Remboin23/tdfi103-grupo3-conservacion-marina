-- ============================================================================
-- PROYECTO SEMESTRAL 2026 - TDFI103 BASES DE DATOS (UNAB)
-- GRUPO 3 - CASO 3: Sistema Integral de Gestión de Centros de Conservación Marina
-- Archivo: sql/01_estructura.sql (Creación de BD, Tablas y Restricciones)
-- Motor: MySQL 8.x
-- ============================================================================

DROP DATABASE IF EXISTS conservacion_marina;
CREATE DATABASE conservacion_marina
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE conservacion_marina;

-- 1. REGION_MARITIMA
CREATE TABLE region_maritima (
    codigoRegion VARCHAR(15) NOT NULL,
    nombreOficial VARCHAR(120) NOT NULL,
    superficieProtegida DECIMAL(12, 2) NOT NULL,
    presupuestoAnual DECIMAL(15, 2) NOT NULL,
    nivelProteccionAmbiental ENUM('Bajo', 'Medio', 'Alto', 'Estricto') NOT NULL,
    CONSTRAINT pk_region_maritima PRIMARY KEY (codigoRegion),
    CONSTRAINT uq_region_nombre UNIQUE (nombreOficial),
    CONSTRAINT chk_region_superficie CHECK (superficieProtegida > 0),
    CONSTRAINT chk_region_presupuesto CHECK (presupuestoAnual >= 0)
) ENGINE=InnoDB;

-- 2. CENTRO_CONSERVACION
CREATE TABLE centro_conservacion (
    codigoCentro VARCHAR(15) NOT NULL,
    nombre VARCHAR(120) NOT NULL,
    fechaCreacion DATE NOT NULL,
    superficieProtegida DECIMAL(12, 2) NOT NULL,
    ubicacion VARCHAR(150) NOT NULL,
    presupuesto DECIMAL(15, 2) NOT NULL,
    capacidadOperativa INT NOT NULL,
    estadoConservacion ENUM('Óptimo', 'Estable', 'En Recuperación', 'Crítico') NOT NULL,
    codigoRegion VARCHAR(15) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT pk_centro_conservacion PRIMARY KEY (codigoCentro),
    CONSTRAINT uq_centro_nombre UNIQUE (nombre),
    CONSTRAINT fk_centro_region FOREIGN KEY (codigoRegion)
        REFERENCES region_maritima(codigoRegion)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT chk_centro_superficie CHECK (superficieProtegida > 0),
    CONSTRAINT chk_centro_presupuesto CHECK (presupuesto >= 0),
    CONSTRAINT chk_centro_capacidad CHECK (capacidadOperativa > 0)
) ENGINE=InnoDB;

-- 3. SECTOR_MARINO (Entidad débil de CENTRO_CONSERVACION)
CREATE TABLE sector_marino (
    codigoCentro VARCHAR(15) NOT NULL,
    numeroInterno INT NOT NULL,
    nombre VARCHAR(120) NOT NULL,
    extension DECIMAL(10, 2) NOT NULL,
    profundidadPromedio DECIMAL(6, 2) NOT NULL,
    temperatura DECIMAL(4, 1) NOT NULL,
    nivelAcceso ENUM('Público', 'Restringido', 'Solo Investigación') NOT NULL,
    biodiversidadEstimada DECIMAL(5, 2) NOT NULL,
    CONSTRAINT pk_sector_marino PRIMARY KEY (codigoCentro, numeroInterno),
    CONSTRAINT fk_sector_centro FOREIGN KEY (codigoCentro)
        REFERENCES centro_conservacion(codigoCentro)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT chk_sector_numero CHECK (numeroInterno > 0),
    CONSTRAINT chk_sector_extension CHECK (extension > 0),
    CONSTRAINT chk_sector_profundidad CHECK (profundidadPromedio >= 0),
    CONSTRAINT chk_sector_temperatura CHECK (temperatura BETWEEN -5.0 AND 45.0),
    CONSTRAINT chk_sector_biodiversidad CHECK (biodiversidadEstimada BETWEEN 0 AND 100)
) ENGINE=InnoDB;

-- 4. ESPECIE_MARINA (Superclase)
CREATE TABLE especie_marina (
    codigoEspecie VARCHAR(15) NOT NULL,
    nombreCientifico VARCHAR(150) NOT NULL,
    nombreComun VARCHAR(120) NOT NULL,
    estadoConservacion ENUM(
        'Preocupación Menor',
        'Casi Amenazada',
        'Vulnerable',
        'En Peligro',
        'En Peligro Crítico'
    ) NOT NULL,
    fechaIncorporacion DATE NOT NULL,
    distribucionGeografica VARCHAR(200) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT pk_especie_marina PRIMARY KEY (codigoEspecie),
    CONSTRAINT uq_especie_cientifico UNIQUE (nombreCientifico)
) ENGINE=InnoDB;

-- 5. PEZ (Subtipo disyunto parcial de ESPECIE_MARINA)
CREATE TABLE pez (
    codigoEspecie VARCHAR(15) NOT NULL,
    largoPromedio DECIMAL(6, 2) NOT NULL,
    profundidadHabitat DECIMAL(6, 2) NOT NULL,
    escamas BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT pk_pez PRIMARY KEY (codigoEspecie),
    CONSTRAINT fk_pez_especie FOREIGN KEY (codigoEspecie)
        REFERENCES especie_marina(codigoEspecie)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT chk_pez_largo CHECK (largoPromedio > 0),
    CONSTRAINT chk_pez_profundidad CHECK (profundidadHabitat >= 0)
) ENGINE=InnoDB;

-- 6. MAMIFERO_MARINO (Subtipo disyunto parcial de ESPECIE_MARINA)
CREATE TABLE mamifero_marino (
    codigoEspecie VARCHAR(15) NOT NULL,
    pesoPromedio DECIMAL(8, 2) NOT NULL,
    periodoGestacional INT NOT NULL,
    alimentacion VARCHAR(100) NOT NULL,
    CONSTRAINT pk_mamifero_marino PRIMARY KEY (codigoEspecie),
    CONSTRAINT fk_mamifero_especie FOREIGN KEY (codigoEspecie)
        REFERENCES especie_marina(codigoEspecie)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT chk_mamifero_peso CHECK (pesoPromedio > 0),
    CONSTRAINT chk_mamifero_gestacion CHECK (periodoGestacional > 0)
) ENGINE=InnoDB;

-- 7. CORAL (Subtipo disyunto parcial de ESPECIE_MARINA)
CREATE TABLE coral (
    codigoEspecie VARCHAR(15) NOT NULL,
    tipoArrecife ENUM('Costero', 'Barrera', 'Atolón', 'Profundo') NOT NULL,
    tasaCrecimiento DECIMAL(5, 2) NOT NULL,
    requiereLuz BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT pk_coral PRIMARY KEY (codigoEspecie),
    CONSTRAINT fk_coral_especie FOREIGN KEY (codigoEspecie)
        REFERENCES especie_marina(codigoEspecie)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT chk_coral_crecimiento CHECK (tasaCrecimiento > 0)
) ENGINE=InnoDB;

-- 8. MONITOREO_ESPECIE (Entidad asociativa SECTOR_MARINO - ESPECIE_MARINA)
CREATE TABLE monitoreo_especie (
    idMonitoreo INT AUTO_INCREMENT NOT NULL,
    codigoCentro VARCHAR(15) NOT NULL,
    numeroInterno INT NOT NULL,
    codigoEspecie VARCHAR(15) NOT NULL,
    fecha DATE NOT NULL,
    cantidadObservada INT NOT NULL,
    condicionesAmbientales VARCHAR(200) NOT NULL,
    observaciones TEXT NULL,
    CONSTRAINT pk_monitoreo_especie PRIMARY KEY (idMonitoreo),
    CONSTRAINT fk_monitoreo_sector FOREIGN KEY (codigoCentro, numeroInterno)
        REFERENCES sector_marino(codigoCentro, numeroInterno)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_monitoreo_especie FOREIGN KEY (codigoEspecie)
        REFERENCES especie_marina(codigoEspecie)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT chk_monitoreo_cantidad CHECK (cantidadObservada >= 0)
) ENGINE=InnoDB;

-- 9. VISITANTE
CREATE TABLE visitante (
    idVisitante INT AUTO_INCREMENT NOT NULL,
    nombres VARCHAR(80) NOT NULL,
    apellidoP VARCHAR(60) NOT NULL,
    apellidoM VARCHAR(60) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    correoPersonal VARCHAR(120) NOT NULL,
    CONSTRAINT pk_visitante PRIMARY KEY (idVisitante),
    CONSTRAINT uq_visitante_correo UNIQUE (correoPersonal)
) ENGINE=InnoDB;

-- 10. ACTIVIDAD
CREATE TABLE actividad (
    idActividad INT AUTO_INCREMENT NOT NULL,
    codigoCentro VARCHAR(15) NOT NULL,
    numeroInterno INT NOT NULL,
    tipoActividad ENUM(
        'Actividad Educativa',
        'Recorrido Guiado',
        'Programa de Observación Marina',
        'Voluntariado Costero'
    ) NOT NULL,
    fechaProgramada DATE NOT NULL,
    horaInicio TIME NOT NULL,
    cupoMaximo INT NOT NULL,
    CONSTRAINT pk_actividad PRIMARY KEY (idActividad),
    CONSTRAINT fk_actividad_sector FOREIGN KEY (codigoCentro, numeroInterno)
        REFERENCES sector_marino(codigoCentro, numeroInterno)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT chk_actividad_cupo CHECK (cupoMaximo > 0)
) ENGINE=InnoDB;

-- 11. PARTICIPACION (Entidad asociativa VISITANTE - ACTIVIDAD)
CREATE TABLE participacion (
    idVisitante INT NOT NULL,
    idActividad INT NOT NULL,
    fechaRegistro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    asistencia BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT pk_participacion PRIMARY KEY (idVisitante, idActividad),
    CONSTRAINT fk_participacion_visitante FOREIGN KEY (idVisitante)
        REFERENCES visitante(idVisitante)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_participacion_actividad FOREIGN KEY (idActividad)
        REFERENCES actividad(idActividad)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 12. EVALUACION (Entidad débil de ACTIVIDAD, vinculada a PARTICIPACION)
CREATE TABLE evaluacion (
    idActividad INT NOT NULL,
    numeroCorrelativo INT NOT NULL,
    idVisitante INT NOT NULL,
    calificacion DECIMAL(3, 1) NOT NULL,
    fecha DATE NOT NULL,
    comentario TEXT NULL,
    CONSTRAINT pk_evaluacion PRIMARY KEY (idActividad, numeroCorrelativo),
    CONSTRAINT uq_evaluacion_visitante_actividad UNIQUE (idVisitante, idActividad),
    CONSTRAINT fk_evaluacion_participacion FOREIGN KEY (idVisitante, idActividad)
        REFERENCES participacion(idVisitante, idActividad)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT chk_evaluacion_correlativo CHECK (numeroCorrelativo > 0),
    CONSTRAINT chk_evaluacion_nota CHECK (calificacion BETWEEN 1.0 AND 7.0)
) ENGINE=InnoDB;

-- 13. TRABAJADOR (Con relación recursiva SUPERVISA 1:N)
CREATE TABLE trabajador (
    rutTrabajador VARCHAR(12) NOT NULL,
    nombreCompleto VARCHAR(150) NOT NULL,
    fechaContratacion DATE NOT NULL,
    cargo ENUM(
        'Administrador',
        'Guardaparques Marino',
        'Conservacionista',
        'Investigador'
    ) NOT NULL,
    rutSupervisor VARCHAR(12) NULL,
    CONSTRAINT pk_trabajador PRIMARY KEY (rutTrabajador),
    CONSTRAINT fk_trabajador_supervisor FOREIGN KEY (rutSupervisor)
        REFERENCES trabajador(rutTrabajador)
        ON UPDATE CASCADE
        ON DELETE SET NULL
) ENGINE=InnoDB;

-- 14. CUENTA_USUARIO (Relación 1:0..1 con TRABAJADOR)
CREATE TABLE cuenta_usuario (
    idCuenta INT AUTO_INCREMENT NOT NULL,
    rutTrabajador VARCHAR(12) NOT NULL,
    fechaCreacion DATE NOT NULL,
    nombreUsuario VARCHAR(50) NOT NULL,
    passwordHash VARCHAR(255) NOT NULL,
    activa BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT pk_cuenta_usuario PRIMARY KEY (idCuenta),
    CONSTRAINT uq_cuenta_trabajador UNIQUE (rutTrabajador),
    CONSTRAINT uq_cuenta_nombre_usuario UNIQUE (nombreUsuario),
    CONSTRAINT fk_cuenta_trabajador FOREIGN KEY (rutTrabajador)
        REFERENCES trabajador(rutTrabajador)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 15. ROL
CREATE TABLE rol (
    idRol INT AUTO_INCREMENT NOT NULL,
    nombreRol VARCHAR(50) NOT NULL,
    descripcion VARCHAR(200) NOT NULL,
    CONSTRAINT pk_rol PRIMARY KEY (idRol),
    CONSTRAINT uq_rol_nombre UNIQUE (nombreRol)
) ENGINE=InnoDB;

-- 16. USUARIO_ROL (Resuelve N:M entre CUENTA_USUARIO y ROL)
CREATE TABLE usuario_rol (
    idCuenta INT NOT NULL,
    idRol INT NOT NULL,
    CONSTRAINT pk_usuario_rol PRIMARY KEY (idCuenta, idRol),
    CONSTRAINT fk_usuariorol_cuenta FOREIGN KEY (idCuenta)
        REFERENCES cuenta_usuario(idCuenta)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_usuariorol_rol FOREIGN KEY (idRol)
        REFERENCES rol(idRol)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 17. ROL_PERMISO (Transforma atributo multivaluado permiso de ROL)
CREATE TABLE rol_permiso (
    idRol INT NOT NULL,
    permiso VARCHAR(60) NOT NULL,
    CONSTRAINT pk_rol_permiso PRIMARY KEY (idRol, permiso),
    CONSTRAINT fk_rolpermiso_rol FOREIGN KEY (idRol)
        REFERENCES rol(idRol)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB;
