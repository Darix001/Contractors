from peewee import *
from datetime import datetime
from base64 import b64encode, b64decode
from orjson import loads, dumps

database = SqliteDatabase('webapp_db.db')

DEFAULT_LIST = []


class JsonField(BlobField):
    db_value = dumps
    python_value = loads


class ImageField(BlobField):
    db_value = staticmethod(b64decode)
    @staticmethod
    def python_value(value:bytes) -> str:
        if value:
            value = b64encode(value)
        return value.decode('utf-8')


class BaseModel(Model):
    class Meta:
        database = database


class Usuarios(BaseModel):
    id_usuario = AutoField(column_name='IDUsuario', null=True)

    usuario = CharField(column_name='Usuario', unique=True)

    foto = ImageField(column_name='Foto', default=b'')
    
    clave = CharField(column_name='Clave')
    
    email = CharField(column_name='Email')
    
    nombre = CharField(column_name='Nombre')
    
    telefono = CharField(12, column_name='Telefono', default='')
    
    titulo_profesional = CharField(column_name='Titulo_Profesional', default='')

    educacion = JsonField(column_name='Educacion', default=DEFAULT_LIST)

    habilidades = JsonField(column_name='Habilidades', default=DEFAULT_LIST)

    experiencia = JsonField(column_name='Experiencia', default=DEFAULT_LIST)

    resumen = TextField(column_name = 'Resumen', default='')

    objetivo = TextField(column_name = 'Objetivo', default='')

    localizacion = CharField(column_name='Localizacion', default='')

    jsons = {
    'experiencia':('nombreEmpresa_','periodoTrabajo_','responsabilidades_'),
    'educacion':("institucion_",'titulo_','periodoEstudio_')}


class Modalidad(BaseModel):
    id_modalidad = AutoField(column_name='IdModalidad', null=True)
    
    nombre = CharField(column_name='Nombre', null=True)


class Publicaciones(BaseModel):
    id_publicacion = AutoField(column_name='IDPublicacion', null=True)
    
    id_usuario = ForeignKeyField(column_name='IDUsuario', field='id_usuario',
        model=Usuarios)
    
    titulo = CharField(column_name='Titulo')
    
    descripcion = CharField(column_name='Descripcion', null=True)
    
    imagen = CharField(column_name='Imagen', null=True)
    
    localizacion = CharField(column_name='Localizacion', null=True)
    
    modalidad = ForeignKeyField(column_name='Modalidad', field='id_modalidad',
        model=Modalidad)
    
    area = CharField(column_name='Area', null=True)
    
    fecha = DateTimeField(column_name='Fecha', default=datetime.now)

    class Meta:
        database = database
        indexes = ((('id_usuario', 'Fecha'), False),)


class Comentario(BaseModel):
    id_comentario = AutoField(column_name='IdComentario', null=True)
    
    id_publicacion = ForeignKeyField(column_name='IdPublicacion',
        field='id_publicacion', model=Publicaciones, null=True)
    
    id_usuario = ForeignKeyField(column_name='IdUsuario',
        field='id_usuario', model=Usuarios, null=True)
    
    comentario = CharField(column_name='Comentario', null=True)


class Estatus(BaseModel):
    id_estatus = AutoField(column_name='IdEstatus', null=True)
    
    nombre = CharField(column_name='Nombre', null=True)


class EtiquetaReaccion(BaseModel):
    id_etiqueta = AutoField(column_name='IdEtiqueta', null=True)
    
    nombre = CharField(column_name='Nombre', null=True)


class Reacciones(BaseModel):
    id_reaccion = AutoField(column_name='IdReaccion', null=True)

    id_publicacion = ForeignKeyField(column_name='IdPublicacion',
        field='id_publicacion', model=Publicaciones, null=True)

    id_usuario = ForeignKeyField(column_name='IdUsuario',
        field='id_usuario', model=Usuarios, null=True)
    
    reaccion = ForeignKeyField(column_name='Reaccion',
        field='id_etiqueta', model=EtiquetaReaccion, null=True)


class Solicitudes(BaseModel):
    id_solicitud = AutoField(column_name='IdSolicitud', null=True)
 
    solicitante = ForeignKeyField(column_name='Solicitante',
        field='id_usuario', model=Usuarios, null=True)
 
    id_publicacion = ForeignKeyField(column_name='IdPublicacion',
        field='id_publicacion', model=Publicaciones, null=True)
    
    estatus = ForeignKeyField(column_name='Estatus',
        field='id_estatus', model=Estatus, null=True)
  
    comentario = CharField(column_name='Comentario', null=True)
  
    calificacion = IntegerField(column_name='Calificacion', null=True)

database.create_tables((Usuarios,Modalidad,Publicaciones,Comentario,Estatus,
    EtiquetaReaccion,Reacciones,Solicitudes))

del dumps, loads, datetime, b64decode