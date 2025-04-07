-- Tabla: TipoArbol
CREATE TABLE IF NOT EXISTS TipoArbol (
    IDTipoArbol INT AUTO_INCREMENT PRIMARY KEY,
    NombreCientifico VARCHAR(150) NOT NULL,
    NombreVulgar VARCHAR(150) NOT NULL,
    Descripcion TEXT,
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla: Rol
CREATE TABLE IF NOT EXISTS Rol (
    IDRol INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(50) NOT NULL,
    Descripcion TEXT,
    Estado INT NOT NULL DEFAULT 1,
    FOREIGN KEY (Estado) REFERENCES Estado(IDEstado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla: UsuarioRol
CREATE TABLE IF NOT EXISTS UsuarioRol (
    IDUsuario INT NOT NULL,
    IDRol INT NOT NULL,
    FechaAsignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (IDUsuario, IDRol),
    FOREIGN KEY (IDUsuario) REFERENCES Usuario(IDUsuario),
    FOREIGN KEY (IDRol) REFERENCES Rol(IDRol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insertar roles básicos
INSERT INTO Rol (Nombre, Descripcion) VALUES 
('Administrador', 'Usuario con acceso total al sistema'),
('Centro', 'Usuario con acceso a la gestión de centros'),
('Usuario', 'Usuario básico con acceso limitado'); 