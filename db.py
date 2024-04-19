from peewee import *
from datetime import datetime
from functools import cached_property
from base64 import b64encode
from orjson import loads, dumps

database = SqliteDatabase('webapp_db.db')

database.foreign_keys = True

DEFAULT_LIST = []


class JsonField(BlobField):
    db_value = dumps

    python_value = loads


class BaseModel(Model):
    class Meta:
        database = database


class Titulo_Profesional(BaseModel):
    id_titulo = AutoField(column_name='titulo_id', null=True)

    nombre = CharField(column_name='nombre', unique=True)
        

class Usuarios(BaseModel):
    id_usuario = AutoField(column_name='IDUsuario', null=True)

    usuario = CharField(column_name='Usuario', unique=True)

    foto = BlobField(column_name='Foto', default=b'')
    
    clave = CharField(column_name='Clave')
    
    email = CharField(column_name='Email')
    
    nombre = CharField(column_name='Nombre')
    
    telefono = CharField(12, column_name='Telefono', default='')
    
    titulo_profesional = ForeignKeyField(column_name='Titulo_Profesional',
        field='id_titulo', model=Titulo_Profesional, default=1)

    educacion = JsonField(column_name='Educacion', default=DEFAULT_LIST)

    habilidades = JsonField(column_name='Habilidades', default=DEFAULT_LIST)

    experiencia = JsonField(column_name='Experiencia', default=DEFAULT_LIST)

    resumen = TextField(column_name = 'Resumen', default='')

    objetivo = TextField(column_name = 'Objetivo', default='')

    localizacion = CharField(column_name='Localizacion', default='')

    intereses = JsonField(column_name='Intereses', default=DEFAULT_LIST)

    jsons = {'educacion':("institucion_",'titulo_','periodoEstudio_'),
    'experiencia':('nombreEmpresa_','periodoTrabajo_','responsabilidades_')}

    with open('templates/default_user.png', 'rb') as image:
        image = b64encode(image.read()).decode()
    
    @cached_property
    def base64(self, default=image) -> str:
        return (b64encode(foto).decode() if (foto:=self.foto) else default)

    del image

    def publicaciones(self, /):
        return Publicaciones.select(Publicaciones, Modalidad, Usuarios
            ).join(Modalidad).switch(Publicaciones).join(Usuarios
            ).where(Publicaciones.id_usuario == self.id_usuario).iterator()


class Modalidad(BaseModel):
    id_modalidad = AutoField(column_name='IdModalidad', null=True)
    
    nombre = CharField(column_name='Nombre', unique=True)


class Publicaciones(BaseModel):
    id_publicacion = AutoField(column_name='IDPublicacion', null=True)
    
    id_usuario = ForeignKeyField(column_name='IDUsuario', field='id_usuario',
        model=Usuarios)
    
    titulo = CharField(column_name='Titulo')
    
    contenido = CharField(column_name='Contenido', default='')
    
    imagen = BlobField(column_name='Imagen', default=b'')
    
    localizacion = CharField(column_name='Localizacion', null=True)
    
    modalidad = ForeignKeyField(column_name='Modalidad', field='id_modalidad',
        model=Modalidad)
    
    area = CharField(column_name='Area', default='')
    
    fecha = DateTimeField(column_name='Fecha', default=datetime.now)

    likes = IntegerField(column_name='Likes', default=0)

    categoria = CharField(column_name='Categoria', default='')

    base64 = property(Usuarios.base64.func)

    @property
    def comentarios(self, /):
        return Comentario.select(Comentario, Publicaciones, Usuarios).join(
        Publicaciones).switch(Comentario).join(Usuarios
        ).where(Comentario.id_publicacion == self.id_publicacion).iterator()

    @classmethod
    def latest(cls, usuario, /):
        return Publicaciones.select(Publicaciones, Usuarios
            ).join(Usuarios).order_by(cls.fecha).iterator()

    class Meta:
        database = database
        indexes = ((('id_usuario', 'Fecha'), False),)


class Comentario(BaseModel):
    id_comentario = AutoField(column_name='IdComentario')
    
    id_publicacion = ForeignKeyField(column_name='IdPublicacion',
        field='id_publicacion', model=Publicaciones)
    
    id_usuario = ForeignKeyField(column_name='IdUsuario',
        field='id_usuario', model=Usuarios)
    
    comentario = CharField(column_name='Comentario')

    fecha = DateTimeField(column_name='Fecha', default=datetime.now)

    class Meta:
        database = database
        indexes = ((('IdPublicacion', 'IdUsuario'), False),)


class Estatus(BaseModel):
    id_estatus = AutoField(column_name='IdEstatus')
    
    nombre = CharField(column_name='Nombre', unique=True)


class EtiquetaReaccion(BaseModel):
    id_etiqueta = AutoField(column_name='IdEtiqueta', null=True)
    
    nombre = CharField(column_name='Nombre', unique=True)


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
    EtiquetaReaccion,Reacciones,Solicitudes,Titulo_Profesional))

del dumps, loads, datetime

# Titulo_Profesional.insert_many(
# [('No studies or incomplete school studies','High School',
# 'Degree',"Master's degree",'technologist')],
# fields = (Titulo_Profesional.nombre,)
# ).execute()

# Modalidad.insert_many([('Select','intern','in person','remote','mixed')],
#     fields=(Modalidad.nombre,)).execute()