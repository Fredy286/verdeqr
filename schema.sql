-- Crear base de datos y usarla
CREATE DATABASE IF NOT EXISTS VerdeQR;
USE VerdeQR;

-- Estado
CREATE TABLE Estado (
    IDEstado INT AUTO_INCREMENT PRIMARY KEY,
    NombreEstado VARCHAR(50) NOT NULL
);

INSERT INTO Estado (NombreEstado) VALUES ('Activo'), ('Inactivo');

-- Usuario
CREATE TABLE Usuario (
    IDUsuario INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Correo VARCHAR(100) NOT NULL,
    Telefono VARCHAR(20),
    Imagen VARCHAR(255),
    Contraseña VARCHAR(100) NOT NULL,
    Estado INT NOT NULL,
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

-- Rol
CREATE TABLE Rol (
    IDRol INT AUTO_INCREMENT PRIMARY KEY,
    NombreRol VARCHAR(50) NOT NULL
);

INSERT INTO Rol (NombreRol) VALUES ('Administrador'), ('Visitante');

-- UsuarioRol
CREATE TABLE UsuarioRol (
    IDUsuarioRol INT AUTO_INCREMENT PRIMARY KEY,
    Usuario INT NOT NULL,
    Rol INT NOT NULL,
    FOREIGN KEY (Usuario) REFERENCES Usuario(IDUsuario),
    FOREIGN KEY (Rol) REFERENCES Rol(IDRol)
);

-- Especie
CREATE TABLE Especie (
    IDEspecie INT AUTO_INCREMENT PRIMARY KEY,
    NombreCientifico VARCHAR(150) NOT NULL,
    NombreVulgar VARCHAR(150) NOT NULL,
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

INSERT INTO Especie (NombreCientifico, NombreVulgar) VALUES
('Mangifera indica', 'Mango'),
('Persea americana', 'Aguacate');

-- UsoArbol
CREATE TABLE UsoArbol (
    IDUso INT AUTO_INCREMENT PRIMARY KEY,
    Especie INT NOT NULL,
    Nombre VARCHAR(150),
    Categoria VARCHAR(50) NOT NULL,
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Especie) REFERENCES Especie(IDEspecie),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

-- UsoMedicinal
CREATE TABLE UsoMedicinal (
    IDUsoMedicinal INT AUTO_INCREMENT PRIMARY KEY,
    Uso INT NOT NULL,
    ParteUtilizada VARCHAR(100),
    Preparacion TEXT,
    EnfermedadesTratadas TEXT,
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Uso) REFERENCES UsoArbol(IDUso),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

-- UsoComestible
CREATE TABLE UsoComestible (
    IDUsoComestible INT AUTO_INCREMENT PRIMARY KEY,
    Uso INT NOT NULL,
    ParteComestible VARCHAR(100),
    FormaConsumo TEXT,
    ValorNutricional TEXT,
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Uso) REFERENCES UsoArbol(IDUso),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

-- UsoMaderable
CREATE TABLE UsoMaderable (
    IDUsoMaderable INT AUTO_INCREMENT PRIMARY KEY,
    Uso INT NOT NULL,
    Dureza VARCHAR(50),
    Resistencia VARCHAR(50),
    UsoFinal VARCHAR(150),
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Uso) REFERENCES UsoArbol(IDUso),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

-- Uso Ornamental
CREATE TABLE UsoOrnamental (
    IDUsoOrnamental INT AUTO_INCREMENT PRIMARY KEY,
    Uso INT NOT NULL,
    CaracteristicasEsteticas VARCHAR(255),
    UbicacionRecomendada VARCHAR(255),
    TipoJardineria VARCHAR(100),
    ColoracionEstacional TEXT,
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Uso) REFERENCES UsoArbol(IDUso),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

-- Uso Artesanal
CREATE TABLE UsoArtesanal (
    IDUsoArtesanal INT AUTO_INCREMENT PRIMARY KEY,
    Uso INT NOT NULL,
    ParteUtilizada VARCHAR(100),
    TipoArtesania VARCHAR(150),
    TecnicasElaboracion TEXT,
    ComunidadesArtesanales VARCHAR(255),
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Uso) REFERENCES UsoArbol(IDUso),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

-- Uso Agroforestal
CREATE TABLE UsoAgroforestal (
    IDUsoAgroforestal INT AUTO_INCREMENT PRIMARY KEY,
    Uso INT NOT NULL,
    SistemaAgroforestal VARCHAR(100),
    BeneficiosAsociados TEXT,
    CultivosCompatibles VARCHAR(255),
    FuncionPrincipal VARCHAR(150),
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Uso) REFERENCES UsoArbol(IDUso),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

-- Uso para Restauración Ecológica
CREATE TABLE UsoRestauracionEcologica (
    IDUsoRestauracion INT AUTO_INCREMENT PRIMARY KEY,
    Uso INT NOT NULL,
    EcosistemaObjetivo VARCHAR(150),
    FuncionEcologica TEXT,
    EspeciesAsociadas VARCHAR(255),
    TasaCrecimiento VARCHAR(50),
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Uso) REFERENCES UsoArbol(IDUso),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

-- Uso Cultural/Ceremonial
CREATE TABLE UsoCulturalCeremonial (
    IDUsoCultural INT AUTO_INCREMENT PRIMARY KEY,
    Uso INT NOT NULL,
    GrupoEtnico VARCHAR(100),
    TipoCeremonia VARCHAR(150),
    SignificadoCultural TEXT,
    ParteUtilizada VARCHAR(100),
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Uso) REFERENCES UsoArbol(IDUso),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

-- Uso Melífero
CREATE TABLE UsoMelifero (
    IDUsoMelifero INT AUTO_INCREMENT PRIMARY KEY,
    Uso INT NOT NULL,
    TipoMiel VARCHAR(100),
    EpocaFloracion VARCHAR(100),
    CalidadPolen VARCHAR(50),
    AtraccionPolinizadores TEXT,
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Uso) REFERENCES UsoArbol(IDUso),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

-- Uso para Protección Ambiental
CREATE TABLE UsoProteccionAmbiental (
    IDUsoProteccion INT AUTO_INCREMENT PRIMARY KEY,
    Uso INT NOT NULL,
    TipoProteccion VARCHAR(100),
    BeneficiosAmbientales TEXT,
    ZonasAplicacion VARCHAR(255),
    CapacidadCapturaCarbon VARCHAR(100),
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Uso) REFERENCES UsoArbol(IDUso),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

-- Uso Tintóreo
CREATE TABLE UsoTintoreo (
    IDUsoTintoreo INT AUTO_INCREMENT PRIMARY KEY,
    Uso INT NOT NULL,
    ParteUtilizada VARCHAR(100),
    ColorObtenido VARCHAR(100),
    MetodoExtraccion TEXT,
    UsosTintes VARCHAR(255),
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Uso) REFERENCES UsoArbol(IDUso),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

-- Uso Oleaginoso
CREATE TABLE UsoOleaginoso (
    IDUsoOleaginoso INT AUTO_INCREMENT PRIMARY KEY,
    Uso INT NOT NULL,
    ParteUtilizada VARCHAR(100),
    TipoAceite VARCHAR(100),
    MetodoExtraccion TEXT,
    PropiedadesAceite TEXT,
    AplicacionesAceite VARCHAR(255),
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Uso) REFERENCES UsoArbol(IDUso),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

-- Uso para Biocombustible
CREATE TABLE UsoBiocombustible (
    IDUsoBiocombustible INT AUTO_INCREMENT PRIMARY KEY,
    Uso INT NOT NULL,
    TipoBiocombustible VARCHAR(100),
    PoderCalorifico VARCHAR(100),
    TasaCrecimiento VARCHAR(50),
    RendimientoPorHectarea VARCHAR(100),
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Uso) REFERENCES UsoArbol(IDUso),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

-- CuriosidadesArbol
CREATE TABLE CuriosidadesArbol (
    IDCuriosidad INT AUTO_INCREMENT PRIMARY KEY,
    Especie INT NOT NULL,
    Descripcion TEXT NOT NULL,
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Especie) REFERENCES Especie(IDEspecie),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

-- InteraccionesEcologicas
CREATE TABLE InteraccionesEcologicas (
    IDInteraccion INT AUTO_INCREMENT PRIMARY KEY,
    Especie INT NOT NULL,
    TipoInteraccion VARCHAR(100),
    Descripcion TEXT,
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Especie) REFERENCES Especie(IDEspecie),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

-- TipoBosque
CREATE TABLE TipoBosque (
    IDTipoBosque INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(100),
    Descripcion TEXT,
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

-- Centro
CREATE TABLE Centro (
    IDCentro INT AUTO_INCREMENT PRIMARY KEY,
    NombreCentro VARCHAR(100),
    Direccion VARCHAR(255),
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

-- Arbol
CREATE TABLE Arbol (
    IDArbol INT AUTO_INCREMENT PRIMARY KEY,
    Especie INT NOT NULL,
    Centro INT NOT NULL,
    TipoBosque INT NOT NULL,
    Caracteristicas TEXT,
    ServiciosEcosistemicos TEXT,
    Imagen VARCHAR(255),
    Descripcion TEXT,
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Especie) REFERENCES Especie(IDEspecie),
    FOREIGN KEY (Centro) REFERENCES Centro(IDCentro),
    FOREIGN KEY (TipoBosque) REFERENCES TipoBosque(IDTipoBosque),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);

-- CodigoQR
CREATE TABLE CodigoQR (
    IDQR INT AUTO_INCREMENT PRIMARY KEY,
    Arbol INT NOT NULL,
    Codigo TEXT,
    Imagen LONGTEXT,
    FechaGeneracion DATETIME,
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Arbol) REFERENCES Arbol(IDArbol),
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
);
-- Tabla: sugerencias
CREATE TABLE IF NOT EXISTS sugerencias (
  IDSugerencia int(11) NOT NULL AUTO_INCREMENT,
  Nombre varchar(100) NOT NULL,
  Email varchar(100) NOT NULL,
  Sugerencia text NOT NULL,
  Fecha datetime DEFAULT current_timestamp(),
  Estado int(11) NOT NULL DEFAULT 1,
  PRIMARY KEY (IDSugerencia),
  KEY Estado (Estado),
  CONSTRAINT sugerencias_ibfk_1 FOREIGN KEY (Estado) REFERENCES estado (IDEstado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabla: tokens_recuperacion
CREATE TABLE IF NOT EXISTS tokens_recuperacion (
  IDToken int(11) NOT NULL AUTO_INCREMENT,
  Usuario int(11) NOT NULL,
  Token varchar(100) NOT NULL,
  FechaExpiracion datetime NOT NULL,
  Estado int(11) NOT NULL DEFAULT 1,
  PRIMARY KEY (IDToken),
  KEY Usuario (Usuario),
  KEY Estado (Estado),
  CONSTRAINT tokens_recuperacion_ibfk_1 FOREIGN KEY (Usuario) REFERENCES Usuario (IDUsuario),
  CONSTRAINT tokens_recuperacion_ibfk_2 FOREIGN KEY (Estado) REFERENCES Estado (IDEstado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;