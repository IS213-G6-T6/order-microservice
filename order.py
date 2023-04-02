#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ

from datetime import datetime
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

CORS(app)  

class Customer(db.Model):
    __tablename__ = 'customer'

    customerID = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(255), nullable=False)
    phone_no = db.Column(db.String(32), nullable=False)

    def json(self):
        dto = {
            'customerID': self.customerID,
            'customer_name': self.customer_name,
            'phone_no': self.phone_no
        }

        return dto

class Order(db.Model):
    __tablename__ = 'orders'

    orderID = db.Column(db.Integer, primary_key=True)
    customerID = db.Column(db.Integer, db.ForeignKey('customer.customerID'), nullable=False, index=True)
    hawkerID = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(32), nullable=False)

    customer = db.relationship('Customer', primaryjoin='Order.customerID == Customer.customerID', backref='orders')

    def json(self):
        dto = {
            'orderID': self.orderID,
            'customerID': self.customerID,
            'hawkerID': self.hawkerID,
            'customer_name': self.customer.customer_name,
            'phone_no': self.customer.phone_no,
            'total_price': self.total_price,
            'status': self.status
        }

        dto['order_items'] = []
        for oi in self.order_items:
            dto['order_items'].append(oi.json())

        return dto


class Order_Items(db.Model):
    __tablename__ = 'order_items'

    orderID = db.Column(db.Integer, db.ForeignKey('orders.orderID', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    itemID = db.Column(db.Integer, primary_key=True, autoincrement=False)
    item_name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    order = db.relationship('Order', primaryjoin='Order_Items.orderID == Order.orderID', backref='order_items')

    def json(self):
        return {'orderID': self.orderID, 'itemID': self.itemID, 'item_name': self.item_name, 'quantity': self.quantity}


@app.route("/order")
def get_all():
    orderlist = Order.query.all()
    if len(orderlist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "orders": [order.json() for order in orderlist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no orders."
        }
    ), 404

@app.route("/order/hawker/<int:hawkerID>")
def get_all_hawker(hawkerID):
    orderlist = Order.query.filter_by(hawkerID=hawkerID).all()
    if len(orderlist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "orders": [order.json() for order in orderlist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no orders with this hawker."
        }
    ), 404


@app.route("/order/<int:orderID>")
def find_by_orderID(orderID):
    order = Order.query.filter_by(orderID=orderID).first()
    if order:
        return jsonify(
            {
                "code": 200,
                "data": order.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "orderID": orderID
            },
            "message": "Order not found."
        }
    ), 404


@app.route("/order", methods=['POST'])
def create_order():
    customerID = request.json.get('customerID', None)
    customer = Customer.query.filter_by(customerID=customerID).first()
    add_customer = 0
    if not customer:
        customer_name = request.json.get('customer_name', None)
        phone_no = request.json.get('phone_no', None)
        add_customer = Customer(customerID=customerID, customer_name=customer_name, phone_no=phone_no)

    hawkerID = request.json.get('hawkerID', None)
    total_price = request.json.get('total_price', None)
    status = request.json.get('status', None)
    order = Order(customerID=customerID, hawkerID=hawkerID, total_price=total_price, status=status)

    order_items = request.json.get('order_items', None)
    for item in order_items:
         order.order_items.append(Order_Items(item_name=item['item_name'],itemID=item['itemID'], quantity=item['quantity']))
         
    try:
        if add_customer:
            db.session.add(add_customer)

        db.session.add(order)
        db.session.commit()

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while creating the order. " + str(e)
            }
        ), 500
    
    print(json.dumps(order.json(), default=str)) # convert a JSON object to a string and print
    print()

    return jsonify(
        {
            "code": 201,
            "data": order.json()
        }
    ), 201


@app.route("/order/<string:orderID>", methods=['PUT'])
def update_order(orderID):
    try:
        order = Order.query.filter_by(orderID=orderID).first()
        if not order:
            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "orderID": orderID
                    },
                    "message": "Order not found."
                }
            ), 404

        # update status
        data = request.get_json()
        if data['status']:
            order.status = data['status']
            db.session.commit()
            return jsonify(
                {
                    "code": 200,
                    "data": order.json()
                }
            ), 200
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "orderID": orderID
                },
                "message": "An error occurred while updating the order. " + str(e)
            }
        ), 500


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": manage orders ...")
    app.run(host='0.0.0.0', port=5000, debug=True)
