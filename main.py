from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, make_response, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO, emit, send

from flask_session import Session
from cookie import *

app = Flask(__name__)

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = 'True'

app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'true'
app.config['SECRET_KEY'] = 'guessmeifyoucan'
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

Session(app)

socketio = SocketIO(app, cors_allowed_origins="*", manage_session=True)
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column('product_id', db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity
        }

class CartEntity(db.Model):
    ref = db.Column('entity_ref', db.Integer, primary_key=True)
    id = db.Column(db.Integer)
    owner = db.Column(db.String(50))

db.create_all()

p1 = Product(name='Video Game', price=59.9, quantity=40)
p2 = Product(name='Mask', price=2.6, quantity=130)
p3 = Product(name='Shampoo', price=13.8, quantity=76)
p4 = Product(name='Cellphone', price=999.99, quantity=24)
p5 = Product(name='Table', price=230.6, quantity=53)
p6 = Product(name='Box', price=7.13, quantity=103)

if len(Product.query.all()) == 0:
    db.session.add(p1)
    db.session.add(p2)
    db.session.add(p3)
    db.session.add(p4)
    db.session.add(p5)
    db.session.add(p6)
    db.session.commit()

def retrieve_cart(cookie):
    entities = CartEntity.query.filter_by(owner=cookie).all()
    ls = []

    for e in entities:
        des = Product.query.filter_by(id=e.id).first().serialize
        ls.append(des)

    return ls

def deserialize(json):
    name = str(json['name'])
    price = float(json['price'])
    quantity = int(json['quantity'])
    return name, price, quantity

@app.route('/shop/', methods=['GET'])
def load():
    objs = [x.serialize for x in Product.query.all()]
    json = jsonify(objs)
    return json


@app.after_request
def shopping_cart(response):
    origin = request.headers.get('Origin')

    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')

    if origin:
        response.headers.add('Access-Control-Allow-Origin', origin)

    return response

@socketio.on('modified-product')
def modify(data):
    id = data['id']

    product = Product.query.filter_by(id=id).first()
    n_name, n_price, n_quantity = deserialize(data)

    product.name = n_name
    product.price = n_price
    product.quantity = n_quantity

    db.session.commit()

    prods = [x.serialize for x in Product.query.all()]
    emit("update_prod", prods, broadcast=True)

@socketio.on('added-product')
def add(data):
    print('data modified')

    n_name, n_price, n_quantity = deserialize(data)
    n_product = Product(name=n_name, price=n_price, quantity=n_quantity)

    db.session.add(n_product)
    db.session.commit()

    prods = [x.serialize for x in Product.query.all()]
    emit("update_prod", prods, broadcast=True)

@socketio.on('removed-product')
def remove(data):
    print('data modified')
    id = data['id']

    Product.query.filter_by(id=id).delete()

    db.session.commit()

    prods = [x.serialize for x in Product.query.all()]
    emit("update_prod", prods, broadcast=True)





@socketio.on('added-to-cart')
def add_to_cart(data):

    id = data['id']
    owner = data['owner']

    cart_entity = CartEntity(id=id, owner=owner)
    db.session.add(cart_entity)
    db.session.commit()

    cart = retrieve_cart(owner)
    emit('update_cart', cart)

@socketio.on('removed-from-cart')
def removed_from_cart(data):
    id = data['id']
    owner = data['owner']

    entities = CartEntity.query.filter_by(owner=owner, id=id).first()
    for e in entities:
        db.session.delete(e)
    db.session.commit()

    cart = retrieve_cart(owner)
    emit('update_cart', cart)

@socketio.on('get-cart')
def get_cart(data):
    owner = data['owner']
    cart = retrieve_cart(owner)
    emit('update_cart', cart)

@socketio.on('checkout')
def get_cart(data):

    owner = data['owner']
    entities = CartEntity.query.filter_by(owner=owner).all()

    for e in entities:
        obj = Product.query.filter_by(id=e.id).first()

        if obj.quantity > 0:
            obj.quantity -= 1
            db.session.delete(e)
        db.session.commit()

    cart = retrieve_cart(owner)
    emit('update_cart', cart)
    prods = [x.serialize for x in Product.query.all()]
    emit("update_prod", prods, broadcast=True)

if __name__ == '__main__':
    socketio.run(app)
