import flask
from pyqrcode import create
from operator import eq
from functools import partial
from io import BytesIO
from collections.abc import MutableMapping
from validate_email import validate_email
from db import database,Usuarios
from itertools import filterfalse
from secrets import token_bytes
from pyzbar.pyzbar import decode
from PIL import Image

app = flask.Flask(__name__)

app.route = partial(app.route,methods = ('POST','GET'))

ENCODE = range(1,1000000)

def key() -> bytes:
    usuario = app.current_user
    return (usuario.email+usuario.clave).translate(ENCODE).encode()


def encode() -> str:
    return create(key()).png_as_base64_str()


def verify(stream) -> bool:
    return key() == decode(Image.open(stream))[0].data


@app.before_request
def connect():
    database.connect()


@app.teardown_request
def close(exc,/):
    if not database.is_closed():
        database.close()


def route(func,/):
    def function(filename=(name:=func.__name__)+'.html',value=None,text=''):
        if (request:=flask.request).method == 'POST':
            value,text = func(request.form)
        return value or flask.render_template(filename,text=text)
    function.__name__ = name
    return app.route('/'+name)(function)


@app.route('/')
def main():
    return app.redirect(app.url_for('Home'))


@route
def Login(form, /): # Cambia la ruta principal a '/login'
    try:
        app.current_user = Usuarios.get(
        Usuarios.usuario == form['Usuario'],Usuarios.clave == form['Clave'])
    except Exception as e:
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
        return app.redirect(app.url_for('QRCode')),None


@route
def Forgot_Password(form, /):
    try:
        app.current_user = usuario = Usuarios.get(
            Usuarios.usuario==form['usuario'])
    except Exception as e:
        return None,'Invalid Username.'

    if (email:=form['email']) != usuario.email:
        return None,'Invalid Email or Phone Number'
    
    return app.redirect(app.url_for('Password')),None


@route
def Password(form, /):
    usuario = app.current_user
    if not verify(flask.request.files.get('key')):
        return None,'Invalid Vefication code'
    if not all(form.values()):
        return None,'There are Missing Fields'
    if form['new_password'] != (key := form['confirm_password']):
        return None,'Passwords does not match.'
    usuario.clave = key
    usuario.save()
    return app.redirect(app.url_for('QRCode')),None


@app.route('/QRCode',methods=('POST','GET'))
def QRCode():
    match flask.request.method:
        case 'POST':
            return app.redirect(app.url_for('Login'))

        case 'GET':
            return flask.render_template('QRCode.html',code=encode())

@route
def Home(form, /):
    pass

@route
def Board(form, /):
    pass

if __name__ == '__main__':
    app.secret_key = encode.__code__.co_code
    app.run(debug=True)