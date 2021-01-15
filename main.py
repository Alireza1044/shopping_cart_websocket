from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, make_response, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO, emit, send

from flask_session import Session
from cookie import *

# import redis
# from flask_kvsession import KVSessionExtension
# from simplekv.memory.redisstore import RedisStore
#
# store = RedisStore(redis.StrictRedis())

app = Flask(__name__)

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = 'True'

app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'true'
app.config['SECRET_KEY'] = 'guessmeifyoucan'
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

Session(app)
# KVSessionExtension(store, app)

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

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'ref': self.ref,
            'id': self.id,
            'owner': self.owner
        }

db.create_all()

p1 = Product(name='dildo', price=98.1, quantity=40)
p2 = Product(name='butt plug', price=128.6, quantity=25)
p3 = Product(name='clip', price=13.8, quantity=164)

if len(Product.query.all()) == 0:
    db.session.add(p1)
    db.session.add(p2)
    db.session.add(p3)
    db.session.commit()



# def list_retrieve():
#     objs = [x.serialize for x in Product.query.all()]
#     json = jsonify(objs)
#     return json

def deserialize(json):
    name = str(json['name'])
    price = float(json['price'])
    quantity = int(json['quantity'])

    return name, price, quantity




# @app.route('/')
# def show_all():
#     return render_template('show_all.html', products=Product.query.all())

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
    print('data modified')
    id = data['id']

    product = Product.query.filter_by(id=id).first()
    n_name, n_price, n_quantity = deserialize(data)

    product.name = n_name
    product.price = n_price
    product.quantity = n_quantity

    db.session.commit()

    a = [x.serialize for x in Product.query.all()]
    print(a)
    emit("update_prod", a, broadcast=True)


@socketio.on('added-product')
def add(data):
    print('data modified')

    n_name, n_price, n_quantity = deserialize(data)
    n_product = Product(name=n_name, price=n_price, quantity=n_quantity)

    db.session.add(n_product)
    db.session.commit()

    a = [x.serialize for x in Product.query.all()]
    print(a)
    emit("update_prod", a, broadcast=True)

@socketio.on('removed-product')
def remove(data):
    print('data modified')
    id = data['id']

    Product.query.filter_by(id=id).delete()

    db.session.commit()

    a = [x.serialize for x in Product.query.all()]
    print(a)
    emit("update_prod", a, broadcast=True)


def retrieve_cart(cookie):
    entities = CartEntity.query.filter_by(owner=cookie).all()
    ls = []

    for e in entities:
        des = Product.query.filter_by(id=e.id).first().serialize
        ls.append(des)

    return ls


@socketio.on('added-to-cart')
def add_to_cart(data):

    print('*************************** add cart \n\n')
    print(data)
    print('\n\n***************************\n\n')

    id = data['id']
    owner = data['owner']

    cart_entity = CartEntity(id=id, owner=owner)
    db.session.add(cart_entity)
    db.session.commit()

    # cart_items = CartEntity.query.filter_by(owner=owner).all()

    # a = [x.serialize for x in CartEntity.query.filter_by(owner=owner).all()]



    # if 'cart' not in session:
    #     session['cart'] = {}
    #     session.modified = True
    #
    #
    #
    # session['cart'][id] = product.serialize
    # session.modified = True
    # app.save_session(session, make_response('dummb'))
    #
    # print('***************************\n\n')
    # print(session)
    # print('\n\n***************************\n\n')

    a = retrieve_cart(owner)
    print('*************************** a \n\n')
    print(a)
    print('\n\n***************************\n\n')
    emit('update_cart', a)

@socketio.on('removed-from-cart')
def removed_from_cart(data):
    print('*************************** rm cart \n\n')
    print(data)
    print('\n\n***************************\n\n')
    id = data['id']
    owner = data['owner']

    entities = CartEntity.query.filter_by(owner=owner, id=id).all()
    for e in entities:
        db.session.delete(e)
    db.session.commit()


    a = retrieve_cart(owner)
    print('*************************** a \n\n')
    print(a)
    print('\n\n***************************\n\n')
    emit('update_cart', a)

@socketio.on('get-cart')
def get_cart(data):
    print('*************************** get_cart\n\n')
    print(data)
    print('\n\n***************************\n\n')
    owner = data['owner']

    a = retrieve_cart(owner)
    print('*************************** a \n\n')
    print(a)
    print('\n\n***************************\n\n')
    emit('update_cart', a)

@socketio.on('checkout')
def get_cart(data):
    print('*************************** checkout\n\n')
    print(data)
    print('\n\n***************************\n\n')
    owner = data['owner']

    entities = CartEntity.query.filter_by(owner=owner).all()
    ls = []

    for e in entities:
        obj = Product.query.filter_by(id=e.id).first()

        if obj.quantity > 0:
            obj.quantity -= 1
            db.session.delete(e)

        db.session.commit()


    a = retrieve_cart(owner)
    emit('update_cart', a)
    b = [x.serialize for x in Product.query.all()]
    emit("update_prod", b, broadcast=True)

if __name__ == '__main__':
    socketio.run(app)
