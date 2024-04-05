from flask import Flask, render_template, request, redirect, url_for
from validate_email import validate_email
from db import database, Usuarios
from itertools import filterfalse

app = Flask(__name__)

methods = ('POST', 'GET')

@app.before_request
def connect():
    database.connect()

@app.teardown_request
def close(exc, /):
    if not database.is_closed():
        database.close()

def route(obj, /):
    def function(filename=(name:=obj.__name__) + '.html', value=None, text=''):
        if (req := request).method == 'POST':
            value, text = obj(req.form)
        return value or render_template(filename, text=text)
    function.__name__ = name
    return app.route('/' + name, methods=methods)(function)

@app.route('/', methods=methods)
def main():
    return redirect(url_for('Home'))

@app.route('/login', methods=methods)
def login(text='Login'):
    if request.method == 'POST':
        form = request.form
        usuario = form.get('Usuario')
        clave = form.get('Clave')
        if not usuario or not clave:
            text = 'Por favor ingrese el usuario y la clave.'
        else:
            try:
                usuario_db = Usuarios.get(
                    Usuarios.usuario == usuario,
                    Usuarios.clave == clave
                )
            except Usuarios.DoesNotExist:
                text = 'Usuario o clave incorrectos.'
            else:
                return redirect(url_for('HomeUser'))
    return render_template('Login.html', text=text)

@route
def Register(form, data={}, /):
    data |= form.items()
    if keys := ','.join(filterfalse(data.get, data)):
        return None, f'Missing fields: {keys}'
    elif not validate_email(data['email']):
        return None, 'The Email address does not exist.'
    elif not Usuarios(**data).save():
        return None, 'Register Error, report to the administrator.'
    else:
        return redirect(url_for('login')), None

@route
def Password(form, /):
    pass

@route
def Home(form, /):
    pass

@route
def HomeUser(form, /):
    pass

if __name__ == '__main__':
    app.secret_key = b'tvqfs!tfdsfu!lfz'
    app.run(debug=True)
