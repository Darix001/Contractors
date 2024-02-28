import PySimpleSQL.db as sql, PySimpleSQL.model as model
from flask import Flask

db = sql.connect('webapp_db.db')

app = Flask(__name__)

@app.route('/')
def main():
    return '<h1>Hello World!</h1>'