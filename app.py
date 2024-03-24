from flask import Flask, request, render_template
from peewee import DoesNotExist
from orjson import loads
from smtplib import SMTP_SSL
from os import urandom
from types import MethodType
from functools import partial
from validate_email import validate_email
from secrets import choice
from db import database,Usuarios
from itertools import filterfalse


app = Flask(__name__)

app.route = partial(app.route,methods = ('POST','GET'))

choice = MethodType(choice, range(10000000, 100000000))

with open('config.json') as config:
    config = loads(config.read())



@app.before_request
def connect():
    database.connect()


@app.teardown_request
def close(exc,/):
    if not database.is_closed():
        database.close()


def route(func,/):
    filename = (name := func.__name__) + '.html'
    def function(value=None, text='', /):
        if request.method == 'POST':
            value,text = func(request.form)
        return value or render_template(filename,text=text)
    function.__name__ = name
    return app.route('/' + name)(function)


@app.route('/')
def main():
    return app.redirect(app.url_for('Home'))


@route
def Login(form, /): # Cambia la ruta principal a '/login'
    try:
        app.current_user = Usuarios.get(
        Usuarios.usuario == form['Usuario'],
        Usuarios.clave == form['Clave'])
    except DoesNotExist as e:
        return None,'Invalid User or password'
    else:
        return app.redirect(app.url_for('Home')),None


@route
def Register(form, data={}, /):
    data|=form.items()
    if keys:=','.join(filterfalse(data.get,data)):
        return None,f'Missing fields: '+keys
    elif not validate_email(data['email']):
        return None,'The Email adress does not exists.'
    elif not (usuario := Usuarios(**data)).save():
        return None,'Register Error, report to the administrator.'
    else:
        app.current_user = usuario
        return app.redirect(app.url_for('email')),None


@route
def Forgot_Password(form, /):
    try:
        app.current_user = usuario = Usuarios.get(
            Usuarios.usuario==form['usuario'],
            Usuarios.email==form['email'])
    except Exception as e:
        return None,'Invalid Username or email.'
    else:
        return app.redirect(app.url_for('email')),None


@app.route('/email')
def email():
    app.code = code = f'{choice()}'
    email = app.current_user.email
    msg = config['msg'].format_map(locals())
    with SMTP_SSL('smtp.gmail.com') as srv:
        srv.login(config['gmail'], config['key'])
        srv.sendmail(config['gmail'], email, msg)
    return app.redirect(app.url_for('Password'))


@route
def Password(form, /):
    if form['code'] != app.code:
        return None,'Invalid Vefication code'
    if not all(form.values()):
        return None,'There are Missing Fields'
    if form['new_password'] != (key := form['confirm_password']):
        return None,'Passwords does not match.'
    usuario = app.current_user
    usuario.clave = key
    usuario.save()
    return app.redirect(app.url_for('Home')),None


@route
def Board(form, /):
    pass


@route
def Home(form, /):
    pass


if __name__ == '__main__':
    app.config.update(
        SECRET_KEY = urandom(32),
        DEBUG = True,
        TESTING = True,
        )
    app.run()