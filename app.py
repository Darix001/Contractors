from flask import Flask,render_template,request
from db import database,Usuarios

app = Flask(__name__)

query = Usuarios.select()

@app.before_request
def _db_connect():
    database.connect()


@app.teardown_request
def _db_close(exc):
    if not database.is_closed():
        database.close()


@app.route('/',methods=('POST','GET'))
def main():
    if request.method == 'POST':
        form = request.form
        exists = query.where(Usuarios.usuario==form['Usuario'],
            Usuarios.clave==form['Clave']).exists()
        if exists:
            return render_template('Home.html')
    return render_template('Login.html')


@app.route("/Register")
def register():
    return render_template('Register.html')


@app.route("/Password")
def password():
    return render_template('Password.html')

if __name__ == '__main__':
    app.run(debug=True)