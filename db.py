from peewee import *

database = SqliteDatabase('webapp_db.db')

class BaseModel(Model):
    class Meta:
        database = database


class Usuarios(BaseModel):
    id_usuario = AutoField(column_name='IDUsuario', null=True)
    nombre = CharField(column_name='Nombre', null=True)
    apellido = CharField(column_name='Apellido', null=True)
    email = CharField(column_name='Email', null=True)
    usuario = CharField(column_name='Usuario', null=True)
    clave = CharField(column_name='Clave', null=True)
    profesion = CharField(column_name='Profesion', null=True)
    telefono = IntegerField(column_name='Telefono', null=True)
    key = BlobField(null=True)


class Modalidad(BaseModel):
    id_modalidad = AutoField(column_name='IdModalidad', null=True)
    nombre = CharField(column_name='Nombre', null=True)


class Publicaciones(BaseModel):
    id_publicacion = AutoField(column_name='IDPublicacion', null=True)
    id_usuario = ForeignKeyField(column_name='IDUsuario', field='id_usuario', model=Usuarios, null=True)
    titulo = CharField(column_name='Titulo', null=True)
    descripcion = CharField(column_name='Descripcion', null=True)
    imagen = CharField(column_name='Imagen', null=True)
    localizacion = CharField(column_name='Localizacion', null=True)
    modalidad = ForeignKeyField(column_name='Modalidad', field='id_modalidad', model=Modalidad, null=True)
    area = CharField(column_name='Area', null=True)


class Comentario(BaseModel):
    id_comentario = AutoField(column_name='IdComentario', null=True)
    id_publicacion = ForeignKeyField(column_name='IdPublicacion', field='id_publicacion', model=Publicaciones, null=True)
    id_usuario = ForeignKeyField(column_name='IdUsuario', field='id_usuario', model=Usuarios, null=True)
    comentario = CharField(column_name='Comentario', null=True)


class Estatus(BaseModel):
    id_estatus = AutoField(column_name='IdEstatus', null=True)
    nombre = CharField(column_name='Nombre', null=True)


class EtiquetaReaccion(BaseModel):
    id_etiqueta = AutoField(column_name='IdEtiqueta', null=True)
    nombre = CharField(column_name='Nombre', null=True)


class Reacciones(BaseModel):
    id_reaccion = AutoField(column_name='IdReaccion', null=True)
    id_publicacion = ForeignKeyField(column_name='IdPublicacion', field='id_publicacion', model=Publicaciones, null=True)
    id_usuario = ForeignKeyField(column_name='IdUsuario', field='id_usuario', model=Usuarios, null=True)
    reaccion = ForeignKeyField(column_name='Reaccion', field='id_etiqueta', model=EtiquetaReaccion, null=True)


class Solicitudes(BaseModel):
    id_solicitud = AutoField(column_name='IdSolicitud', null=True)
    solicitante = ForeignKeyField(column_name='Solicitante', field='id_usuario', model=Usuarios, null=True)
    id_publicacion = ForeignKeyField(column_name='IdPublicacion', field='id_publicacion', model=Publicaciones, null=True)
    estatus = ForeignKeyField(column_name='Estatus', field='id_estatus', model=Estatus, null=True)
    comentario = CharField(column_name='Comentario', null=True)
    calificacion = IntegerField(column_name='Calificacion', null=True)

database.create_tables((Usuarios,Modalidad,Publicaciones,Comentario,Estatus,
    EtiquetaReaccion,Reacciones,Solicitudes))