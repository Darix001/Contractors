from flask import Flask, render_template, request, redirect, url_for
from db import database, Usuarios, Publicaciones, Titulo_Profesional, Comentario
from functools import partial, update_wrapper
from validate_email import validate_email
from peewee import IntegrityError
from os import urandom, environ
from smtplib import SMTP_SSL
from orjson import loads

app = Flask(__name__)

app.route = partial(app.route, methods=('POST', 'GET'))

with open('config.json', 'rb') as config:
    config = loads(config.read())


def getcode() -> int:
    return int.from_bytes(urandom(3))

@app.before_request
def connect():
    database.connect()

@app.teardown_request
def close(exc, /):
    if not database.is_closed():
        database.close()

def post(obj=None, /, text='', forward="HomeUser"):
    if obj:
        name = obj.__name__
        filename = name + '.html'
        def function(text=text, /):
            if request.method == 'POST':
                if not (text := obj(request.form)):
                    return redirect(url_for(forward or app.forward))
            return render_template(filename, text=text)
        return app.route('/' + name)(update_wrapper(function, obj))
    return partial(post, text=text, forward=forward)

@app.route('/')
def main():
    return redirect(url_for('Home'))

@post(text='Login')
def Login(form, /):
    try:
        app.current_user = Usuarios.get(**form)
    except Usuarios.DoesNotExist:
        return 'Incorrect user or password'

@post(text = 'Register a new account', forward = 'email')
def Register(form, /):
    app.current_user = usuario = Usuarios(**form)
    if not validate_email(usuario.email):
        return 'The Email address does not exist'
    try:
        usuario.save()
    except IntegrityError:
        return 'This Username already exists'
    else:
        app.forward = 'HomeUser'

@app.route('/email/<name>')
def email(name:str):
    app.code = code = f'{getcode()}'
    email = app.current_user.email
    msg = config['msg'].format_map(locals())
    with SMTP_SSL('smtp.gmail.com') as srv:
        srv.login(config['gmail'], config['key'])
        srv.sendmail(config['gmail'], email, msg)
    return redirect(url_for('Code'))

@post(forward=None)
def Code(form, /):
    if form['code'] != app.code:
        return 'Invalid Verification Code'

@post(forward='email')
def Forgot_Password(form, /):
    try:
        app.current_user = Usuarios.get(**form)
    except Usuarios.DoesNotExist:
        return 'Invalid Username or Email'
    else:
        app.forward = 'Password'

@post
def Password(form, /):
    if not all(form.values()):
        return 'There are Missing Fields'
    if form['new_password'] != (key := form['confirm_password']):
        return 'Passwords does not match.'
    usuario = app.current_user
    usuario.clave = key
    usuario.save()

@app.route('/close')
def close():
    del app.current_user
    return redirect(url_for('Home'))

@post
def Home(form, /):
    pass

def user_page(obj):
    name = obj.__name__
    filename = name + '.html'
    def function():
        if not (usuario := getattr(app, 'current_user', None)):
            return redirect(url_for('Login'))
        if request.method == 'POST':
            obj(request.form, usuario)
            return redirect(url_for("HomeUser"))
        return render_template(filename, usuario = usuario)
    return app.route('/' + name)(update_wrapper(function, obj))

@user_page
def Edit(form, usuario, /):
    data = usuario.__data__
    data['habilidades'] = dict.pop(form, 'habilidades', ())
    if (t := dict.pop(form, 'titulo_profesional')[0]).isdigit():
        usuario.titulo_profesional = Titulo_Profesional.get_by_id(int(t))
    data|={k:(v if k.endswith('_') else v[0]) for k, v in dict.items(form)}
    if foto := request.files.get('foto'):
        data['foto'] = foto.read()
        del usuario.base64
    for field, keys in usuario.jsons.items():
        data[field] = [*zip(*map(data.pop, keys))]
    usuario.save()

@user_page
def HomeUser(form, usuario,/):
    save_publication_or_comment(form, usuario)

@user_page
def UserProfile(form, usuario,/):
    save_publication_or_comment(form, usuario)

def save_publication_or_comment(form, usuario,/):
    if 'comentario' in form:
        return Comentario(**form).save()
    if imagen := request.files.get('imagen'):
        dict.update(form, imagen=imagen.read())
    Publicaciones(**form, id_usuario=usuario.id_usuario).save()


if __name__ == '__main__':
    app.config.update(
        SECRET_KEY = urandom(32),
        DEBUG = True,
        TESTING = True
        )
    app.run(port=5555)