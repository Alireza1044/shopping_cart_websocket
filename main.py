from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, session, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO, emit, send
from sqlalchemy.orm.attributes import flag_modified

app = Flask(__name__, template_folder="/template")
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'true'
app.config['SECRET_KEY'] = 'guessmeifyoucan'
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
socketio = SocketIO(app, cors_allowed_origins="*")
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


def list_retrieve():
    objs = [x.serialize for x in Product.query.all()]
    json = jsonify(objs)
    return json

def deserialize(json):
    name = str(json['name'])
    price = float(json['price'])
    quantity = int(json['quantity'])

    return name, price, quantity

db.create_all()

p1 = Product(name='dildo', price=98.1, quantity=40)
p2 = Product(name='butt plug', price=128.6, quantity=25)
p3 = Product(name='clip', price=13.8, quantity=164)

db.session.add(p1)
db.session.add(p2)
db.session.add(p3)
db.session.commit()


# @app.route('/')
# def show_all():
#     return render_template('show_all.html', products=Product.query.all())

@app.route('/shop/', methods=['GET'])
def load():
    return list_retrieve()


@app.after_request
def shopping_cart(response):
    origin = request.headers.get('Origin')

    # if 'cart' not in session:
    #     session['cart'] = {}
    #     session.modified = True
    #
    # session.modified = True

    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')

    if origin:
        response.headers.add('Access-Control-Allow-Origin', origin)
    return response


@socketio.on('connect')
def test_connect():
    print('someone connected to websocket')
    a = [x.serialize for x in Product.query.all()]
    # print(a)
    emit("update_prod", a)


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

    # db.session.delete(product)
    db.session.commit()

    a = [x.serialize for x in Product.query.all()]
    print(a)
    emit("update_prod", a, broadcast=True)


@socketio.on('added-to-cart')
def add_to_cart(data):

    id = data['id']

    product = Product.query.filter_by(id=id).first()

    if 'cart' not in session:
        session['cart'] = {}
        session.modified = True

    session['cart'][id] = product.serialize
    session.modified = True

    a = [session['cart']]
    # print("A=   ", a)
    emit('update_cart', a)


@socketio.on('removed-from-cart')
def removed_from_cart(data):
    # print('***************************\n\n')
    print(data)
    # print('\n\n***************************\n\n')
    id = data['id']

    session['cart'].pop(id, None)
    session.modified = True

    a = [session['cart']]
    # print("A=   ", a)
    emit('update_cart', a)


if __name__ == '__main__':
    socketio.run(app, port=5000)
