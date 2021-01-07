from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO, emit, send

app = Flask(__name__, template_folder="/Users/alireza/Desktop/Code/991/Internet Engineering/HW4/HW4/template")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'true'
app.config['SECRET_KEY'] = 'guessmeifyoucan'
socketio = SocketIO(app, cors_allowed_origins="*")
db = SQLAlchemy(app)
CORS(app)


class products(db.Model):
    id = db.Column('product_id', db.Integer, primary_key=True)
    name = db.Column(db.Integer)
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)

    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity


db.create_all()


@app.route('/')
def show_all():
    return render_template('show_all.html', products=products.query.all())


@socketio.on('connect')
def test_connect():
    print('someone connected to websocket')


if __name__ == '__main__':
    socketio.run(app, port=5000)
