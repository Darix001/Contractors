-- create database WEBAPP_DB

CREATE TABLE Usuarios(
    IDUsuario INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre VARCHAR(20),
    Apellido VARCHAR(30),
    Email VARCHAR(50),
    Usuario VARCHAR(50),
    Clave VARCHAR(150),
    Profesion VARCHAR(20),
    Telefono INT
);

CREATE TABLE Modalidad (
    IdModalidad INT PRIMARY KEY,
    Nombre VARCHAR(20)
);

CREATE TABLE Publicaciones (
    IDPublicacion INTEGER PRIMARY KEY AUTOINCREMENT,
    IDUsuario INT,
    Titulo VARCHAR(50),
    Descripcion VARCHAR(150),
    Imagen VARCHAR(150),
    Localizacion VARCHAR(200),
    Modalidad INT,
    Area VARCHAR(50),
    FOREIGN KEY (IDUsuario) REFERENCES Usuarios(IDUsuario),
    FOREIGN KEY (Modalidad) REFERENCES Modalidad(IdModalidad)
);

CREATE TABLE Estatus (
    IdEstatus INT PRIMARY KEY,
    Nombre VARCHAR(20)
);

CREATE TABLE EtiquetaReaccion (
    IdEtiqueta INT PRIMARY KEY,
    Nombre VARCHAR(20)
);

CREATE TABLE Reacciones (
    IdReaccion INT PRIMARY KEY,
    IdPublicacion INT,
    IdUsuario INT,
    Reaccion INT,
    FOREIGN KEY (IdPublicacion) REFERENCES Publicaciones(IDPublicacion),
    FOREIGN KEY (IdUsuario) REFERENCES Usuarios(IDUsuario),
    FOREIGN KEY (Reaccion) REFERENCES EtiquetaReaccion(IdEtiqueta)
);
CREATE TABLE Comentario (
    IdComentario INT PRIMARY KEY,
    IdPublicacion INT,
    IdUsuario INT,
    Comentario VARCHAR(200),
    FOREIGN KEY (IdPublicacion) REFERENCES Publicaciones(IDPublicacion),
    FOREIGN KEY (IdUsuario) REFERENCES Usuarios(IDUsuario)
);

CREATE TABLE Solicitudes (
    IdSolicitud INT PRIMARY KEY,
    Solicitante INT,
    IdPublicacion INT,
    Estatus INT,
    Comentario VARCHAR(200),
    Calificacion INT,
    FOREIGN KEY (Solicitante) REFERENCES Usuarios(IDUsuario),
    FOREIGN KEY (IdPublicacion) REFERENCES Publicaciones(IDPublicacion),
    FOREIGN KEY (Estatus) REFERENCES Estatus(IdEstatus)
);
