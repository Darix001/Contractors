from flask import Flask, render_template, request, redirect, url_for
from validate_email import validate_email
from functools import partial, wraps
from db import database, Usuarios
from itertools import filterfalse
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

def route(obj, /):
    filename = (name := obj.__name__) + '.html'
    @wraps(obj)
    def function(value=None, text='', /, **kwargs):
        if request.method == 'POST':
            value, text = obj(request.form, kwargs)
        return value or render_template(filename, text=text)
    return app.route('/' + name)(function)

@app.route('/')
def main():
    return redirect(url_for('Home'))

@app.route('/Login')
def Login(text='Login'):
    if request.method == 'POST':
        form = request.form
        usuario = form.get('Usuario')
        clave = form.get('Clave')
        if not (usuario and clave):
            text = 'Please Introduce Username and Password'
        else:
            try:
                app.current_user = Usuarios.get(
                    Usuarios.usuario == usuario,
                    Usuarios.clave == clave
                )
            except Usuarios.DoesNotExist:
                text = 'Incorrect user or password'
            else:
                return redirect(url_for('HomeUser'))
    return render_template('Login.html', text=text)

@route
def Register(form, data, /):
    app.current_user = usuario = Usuarios(**form)
    if keys := ','.join(filterfalse(form.get, form)):
        return None, f'Missing fields: {keys}'
    elif not validate_email(usuario.email):
        return None, 'The Email address does not exist.'
    elif not usuario.save():
        return None, 'Register Error, report to the administrator.'
    else:
        return redirect(url_for('email', name = 'HomeUser')),None

@app.route('/email/<name>')
def email(name:str):
    app.code = code = f'{choice()}'
    email = app.current_user.email
    msg = config['msg'].format_map(locals())
    with SMTP_SSL('smtp.gmail.com') as srv:
        srv.login(config['gmail'], config['key'])
        srv.sendmail(config['gmail'], email, msg)
    return redirect(url_for('Code', name = name))

@route
def Code(form, data, /):
    if form['code'] == app.code:
        return redirect(url_for(request.args.get('name'))),None
    return 'Invalid Verification Code',None

@route
def Forgot_Password(form, data, /):
    try:
        app.current_user = Usuarios.get(
            Usuarios.usuario == form['usuario'],
            Usuarios.email == form['email']
        )
    except Usuarios.DoesNotExist:
        return 'Invalid Username or Email',None
    else:
        return redirect(url_for('email', name='Password')),None

@route
def Password(form, data, /):
    if not all(form.values()):
        return None,'There are Missing Fields'
    if form['new_password'] != (key := form['confirm_password']):
        return None,'Passwords does not match.'
    usuario = app.current_user
    usuario.clave = key
    usuario.save()
    return redirect(url_for('HomeUser')),None

@route
def Home(form,/):
    pass

@app.route('/HomeUser')
def HomeUser():
    match request.method:
        case 'GET':
            data = app.current_user.__data__
            return render_template('HomeUser.html', **data)

        case 'POST':
            pass

if __name__ == '__main__':
    app.config.update(
        SECRET_KEY = urandom(32),
        DEBUG = True,
        TESTING = True,
        )
    app.run()