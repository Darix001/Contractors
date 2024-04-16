BEGIN TRANSACTION

CREATE TABLE "comentario" (
	"IdComentario" INTEGER PRIMARY KEY,
	 "IdPublicacion" INTEGER,
	 "IdUsuario" INTEGER,
	 "Comentario" VARCHAR(255),
	 FOREIGN KEY ("IdPublicacion") REFERENCES "publicaciones" ("IDPublicacion"),
	 FOREIGN KEY ("IdUsuario") REFERENCES "usuarios" ("IDUsuario")
	 )

CREATE TABLE "estatus" (
	"IdEstatus" INTEGER PRIMARY KEY,
	 "Nombre" VARCHAR(255)
	 )

CREATE TABLE "etiquetareaccion" (
	"IdEtiqueta" INTEGER PRIMARY KEY,
	 "Nombre" VARCHAR(255)
	 )

CREATE TABLE "modalidad" (
	"IdModalidad" INTEGER PRIMARY KEY,
	 "Nombre" VARCHAR(255)
	 )

CREATE TABLE "publicaciones" (
	 "IDPublicacion" INTEGER PRIMARY KEY,
	 "IDUsuario" INTEGER,
	 "Titulo" VARCHAR(255),
	 "Descripcion" VARCHAR(255),
	 "Imagen" VARCHAR(255),
	 "Localizacion" VARCHAR(255),
	 "Modalidad" INTEGER,
	 "Area" VARCHAR(255),
	 "Fecha" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	 "Educacion" VARCHAR(255),
	 "Habilidades" VARCHAR(255),
	 "Notas" VARCHAR(255),
	 FOREIGN KEY ("IDUsuario") REFERENCES "usuarios" ("IDUsuario"),
	 FOREIGN KEY ("Modalidad") REFERENCES "modalidad" ("IdModalidad")
	 )

CREATE TABLE "reacciones" (
	"IdReaccion" INTEGER PRIMARY KEY,
	 "IdPublicacion" INTEGER,
	 "IdUsuario" INTEGER,
	 "Reaccion" INTEGER,
	 FOREIGN KEY ("IdPublicacion") REFERENCES "publicaciones" ("IDPublicacion"),
	 FOREIGN KEY ("IdUsuario") REFERENCES "usuarios" ("IDUsuario"),
	 FOREIGN KEY ("Reaccion") REFERENCES "etiquetareaccion" ("IdEtiqueta")
	 )

CREATE TABLE "solicitudes" (
	"IdSolicitud" INTEGER PRIMARY KEY,
	 "Solicitante" INTEGER,
	 "IdPublicacion" INTEGER,
	 "Estatus" INTEGER,
	 "Comentario" VARCHAR(255),
	 "Calificacion" INTEGER,
	 FOREIGN KEY ("Solicitante") REFERENCES "usuarios" ("IDUsuario"),
	 FOREIGN KEY ("IdPublicacion") REFERENCES "publicaciones" ("IDPublicacion"),
	 FOREIGN KEY ("Estatus") REFERENCES "estatus" ("IdEstatus")
	 )

CREATE TABLE "usuarios" (
	"IDUsuario" INTEGER PRIMARY KEY,
	 "Nombre" VARCHAR(255),
	 "Apellido" VARCHAR(255),
	 "Email" VARCHAR(255),
	 "Usuario" VARCHAR(255),
	 "Clave" VARCHAR(255),
	 "Profesion" VARCHAR(255),
	 "Telefono" INTEGER
	 )

CREATE UNIQUE INDEX "usuarios_Usuario" ON "usuarios" ("Usuario")

CREATE INDEX "publicaciones_IDUsuario" ON "publicaciones" ("IDUsuario")

CREATE INDEX "publicaciones_Modalidad" ON "publicaciones" ("Modalidad")

CREATE INDEX "publicaciones_IDUsuario_Fecha" ON "publicaciones" ("IDUsuario","Fecha")

CREATE INDEX "comentario_IdPublicacion" ON "comentario" ("IdPublicacion")

CREATE INDEX "comentario_IdUsuario" ON "comentario" ("IdUsuario")

CREATE INDEX "reacciones_IdPublicacion" ON "reacciones" ("IdPublicacion")

CREATE INDEX "reacciones_IdUsuario" ON "reacciones" ("IdUsuario")

CREATE INDEX "reacciones_Reaccion" ON "reacciones" ("Reaccion")

CREATE INDEX "solicitudes_Solicitante" ON "solicitudes" ("Solicitante")

CREATE INDEX "solicitudes_IdPublicacion" ON "solicitudes" ("IdPublicacion")

CREATE INDEX "solicitudes_Estatus" ON "solicitudes" ("Estatus")

COMMIT