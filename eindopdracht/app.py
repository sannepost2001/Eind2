import mysql.connector
from flask import Flask, request, render_template, make_response

app = Flask(__name__)


@app.route('/')
def home():
    resp = make_response(render_template('home.html'))
    return resp


@app.route('/<path:filename>', methods=['GET'])
def pagina(filename):
    resp = make_response(render_template(filename))
    return resp


if __name__ == '__main__':
    app.run()
