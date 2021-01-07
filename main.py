from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO, emit, send

app = Flask(__name__, template_folder="/template")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'true'
app.config['SECRET_KEY'] = 'guessmeifyoucan'
socketio = SocketIO(app, cors_allowed_origins="*")
db = SQLAlchemy(app)


class Product(db.Model):
    id = db.Column('product_id', db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)

    # def __init__(self, name, price, quantity):
    #     self.name = name
    #     self.price = price
    #     self.quantity = quantity

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity
        }


db.create_all()

p1 = Product(name='dildo', price=98.1, quantity=40)
p2 = Product(name='butt plug', price=128.6, quantity=25)
p3 = Product(name='clip', price=13.8, quantity=164)

db.session.add(p1)
db.session.add(p2)
db.session.add(p3)
db.session.commit()


@app.route('/')
def show_all():
    return render_template('show_all.html', products=Product.query.all())


@socketio.on('connect')
def test_connect():
    print('someone connected to websocket')
    a = [x.serialize for x in Product.query.all()]
    print(a)
    emit("update_prod", a)


@socketio.on('added-to-cart')
def add_to_cart(data):
    print(data)
    a = [x.serialize for x in Product.query.filter_by(id=data['id'])]
    print("A=   ", a)
    emit('update_cart', a)


if __name__ == '__main__':
    socketio.run(app, port=5000)
