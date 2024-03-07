import flask
from validate_email import validate_email
from db import database,Usuarios
from itertools import filterfalse

app = flask.Flask(__name__)

methods = ('POST','GET')

@app.before_request
def connect():
    database.connect()


@app.teardown_request
def close(exc,/):
    if not database.is_closed():
        database.close()


def route(obj,/):
    def function(filename=(name:=obj.__name__)+'.html',value=None,text=''):
        if (request:=flask.request).method == 'POST':
            value,text = obj(request.form)
        return value or flask.render_template(filename,text=text)
    function.__name__ = name
    return app.route('/'+name, methods = methods)(function)


@app.route('/', methods = methods)
def main(text = 'Login'):
    if (request:=flask.request).method == 'POST':
        form = request.form
        try:
            usuario = Usuarios.get(Usuarios.usuario==form['Usuario'],
                Usuarios.clave==form['Clave'])
        except Exception as e:
            text = 'Invalid User or password'
        else:
            return app.redirect(app.url_for('Home'))
    return flask.render_template('Login.html',text=text)


@route
def Register(form, data={}, /):
    data|=form.items()
    if keys:=','.join(filterfalse(data.get,data)):
        return None,f'Missing fields: '+keys
    elif not validate_email(data['email']):
        return None,'The Email adress does not exists.'
    elif not Usuarios(**data).save():
        return None,'Register Error, report to the administrator.'
    else:
        return app.redirect(app.url_for('main')),None

@route
def Password(form,/):
    pass

@route
def Home(form,/):
    pass

if __name__ == '__main__':
    app.secret_key = b'tvqfs!tfdsfu!lfz'
    app.run(debug=True)