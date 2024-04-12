from flask import Flask, render_template, request, redirect, url_for
from db import database, Usuarios, Publicaciones
from validate_email import validate_email
from functools import partial, wraps
from itertools import filterfalse
from peewee import IntegrityError
from smtplib import SMTP_SSL
from types import MethodType
from secrets import choice
from orjson import loads
from os import urandom

app = Flask(__name__)

app.route = partial(app.route, methods = ('POST','GET'))

choice = MethodType(choice, range(10000000, 100000000))

with open('config.json', 'rb') as config:
    config = loads(config.read())


@app.before_request
def connect():
    database.connect()

@app.teardown_request
def close(exc, /):
    if not database.is_closed():
        database.close()

def post(obj=None, /, text=''):
    if obj:
        filename = (name := obj.__name__) + '.html'
        @wraps(obj)
        def function(text=text, /):
            if request.method == 'POST':
                text = obj(request.form)
                if not isinstance(text, str):
                    return text
            return render_template(filename, text=text)
        return app.route('/' + name)(function)
    else:
        return partial(post, text=text)

@app.route('/')
def main():
    return redirect(url_for('Home'))

@post(text='Login')
def Login(form, /):
    usuario = form.get('Usuario')
    clave = form.get('Clave')
    if not (usuario and clave):
        return 'Please Introduce Username and Password'
    else:
        try:
            app.current_user = Usuarios.get(
                Usuarios.usuario == usuario,
                Usuarios.clave == clave
            )
        except Usuarios.DoesNotExist:
            return 'Incorrect user or password'
        else:
            return redirect(url_for('HomeUser'))

@post(text = 'Register a new account')
def Register(form, /):
    app.current_user = usuario = Usuarios(**form)
    if keys := ','.join(filterfalse(form.get, form)):
        return  f'Missing fields: {keys}'
    elif not validate_email(usuario.email):
        return  'The Email address does not exist.'
    else:
        try:
            usuario.save()
        except IntegrityError:
            return  'Invalid Username'
    return redirect(url_for('email', name = 'Password'))

@app.route('/email/<name>')
def email(name:str):
    app.code = code = f'{choice()}'
    email = app.current_user.email
    msg = config['msg'].format_map(locals())
    with SMTP_SSL('smtp.gmail.com') as srv:
        srv.login(config['gmail'], config['key'])
        srv.sendmail(config['gmail'], email, msg)
    return redirect(url_for('Code', name = name))

@post
def Code(form, /):
    if form['code'] == app.code:
        return redirect(url_for(request.args.get('name')))
    return 'Invalid Verification Code'

@post
def Forgot_Password(form, /):
    try:
        app.current_user = Usuarios.get(
            Usuarios.usuario == form['usuario'],
            Usuarios.email == form['email']
        )
    except Usuarios.DoesNotExist:
        return 'Invalid Username or Email'
    else:
        return redirect(url_for('email', name = 'Password'))

@post
def Password(form, /):
    if not all(form.values()):
        return 'There are Missing Fields'
    if form['new_password'] != (key := form['confirm_password']):
        return 'Passwords does not match.'
    usuario = app.current_user
    usuario.clave = key
    usuario.save()
    return redirect(url_for('HomeUser'))

@post
def Home(form, /):
    pass

@post
def Edit(form, /):
    usuario = app.current_user
    usuario.__data__.update(form)
    usuario.save()
    return redirect(url_for('HomeUser'))

@app.route('/HomeUser')
def HomeUser():
    data = app.current_user.__data__
    return render_template('HomeUser.html', **data)


if __name__ == '__main__':
    app.config.update(
        SECRET_KEY = urandom(32),
        DEBUG = True,
        TESTING = True,
        )
    app.run()