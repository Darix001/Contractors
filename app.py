from validate_email import validate_email
from flask import Flask,render_template,request,flash,redirect,url_for
from db import database,Usuarios
from itertools import filterfalse

app = Flask(__name__)

methods = ('POST','GET')

@app.before_request
def connect():
    database.connect()


@app.teardown_request
def close(exc,/):
    if not database.is_closed():
        database.close()


def route(obj,/):
    def function(filename=(name:=obj.__name__)+'.html',value=None):
        if request.method == 'POST':
            value = obj(request.form)
        return value or render_template(filename)
    function.__name__ = name
    return app.route('/'+name, methods = methods)(function)


@app.route('/', methods = methods)
def main():
    if request.method == 'POST':
        form = request.form
        usuario = Usuarios.get(Usuarios.usuario==form['Usuario'],
            Usuarios.clave==form['Clave'])
        if usuario:
            return render_template('Home.html')
    return render_template('Login.html')


@route
def Register(form,data={},/):
    data|=form.items()
    if keys:=','.join(filterfalse(data.get,data)):
        flash(f'Missing fields: '+keys,'error')
    elif not validate_email(data['email']):
        flash('The Email adress does not exists.')
    elif not Usuarios(**data).save():
        flash('Register Error, report to the administrator.')
    else:
        flash('Registered! Welcome to Contractors.')
        return redirect(url_for('main'))

@route
def Password(form,/):
    pass

@route
def Home(form,/):
    pass

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug=True)