#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class RestaurantListResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [restaurant.to_dict_exclude_pizzas() for restaurant in restaurants]

class RestaurantResource(Resource):
    def get(self, id):
        restaurant = db.session.get(Restaurant, id)
        if restaurant:
            return restaurant.to_dict(rules=('restaurant_pizzas', 'restaurant_pizzas.pizza'))
        else:
            return {"error": "Restaurant not found"}, 404

    def delete(self, id):
        restaurant = db.session.get(Restaurant, id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return '', 204
        else:
            return {"error": "Restaurant not found"}, 404

class PizzaListResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [pizza.to_dict_exclude_restaurant_pizzas() for pizza in pizzas]

class RestaurantPizzaResource(Resource):
    def post(self):
        data = request.get_json()
        price = data.get('price')
        pizza_id = data.get('pizza_id')
        restaurant_id = data.get('restaurant_id')

        if not 1 <= price <= 30:
            return {"errors": ["validation errors"]}, 400

        pizza = db.session.get(Pizza, pizza_id)
        restaurant = db.session.get(Restaurant, restaurant_id)
        if not pizza or not restaurant:
            return {"errors": ["Pizza or Restaurant not found"]}, 404

        restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(restaurant_pizza)
        db.session.commit()

        return restaurant_pizza.to_dict(rules=('restaurant', 'pizza')), 201

api.add_resource(RestaurantListResource, '/restaurants')
api.add_resource(RestaurantResource, '/restaurants/<int:id>')
api.add_resource(PizzaListResource, '/pizzas')
api.add_resource(RestaurantPizzaResource, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)