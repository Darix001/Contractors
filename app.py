import flask, smtplib
from os import urandom
from types import MethodType
from functools import partial
from validate_email import validate_email
from secrets import choice
from db import database,Usuarios
from itertools import filterfalse
from email.mime.text import MIMEText

app = flask.Flask(__name__)

app.route = partial(app.route, methods = ('POST','GET'))

choice = MethodType(choice, range(10000000, 100000000))

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
    msg = MIMEText(f'Your Verification Code is: '+code)
    msg['To'] = email = app.current_user.email
    msg['From'] = me = 'contractors.webapp@gmail.com'
    msg['Subject'] = 'Change Password'
    with smtplib.SMTP_SSL('smtp.gmail.com') as server:
        s.login(me,'fvskeowwfhrhxpqn')
        s.sendmail(me,email,msg.as_string())
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


if __name__ == '__main__':
    app.config.update(
        SECRET_KEY = urandom(),
        DEBUG = True,
        TESTING = True)
    app.run()