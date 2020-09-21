from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required

from security import authenticate, identity

app = Flask(__name__)
app.secret_key = 'test_app'
api = Api(app)

jwt = JWT(app, authenticate, identity) # /auth

items = []

class Item(Resource):
	@jwt_required()
	def get(self, name):
		item = next(filter(lambda x: x['name'] == name, items), None)
		return {'item': item}, 200 if item else 404

	@jwt_required()
	def post(self, name):
		parser = reqparse.RequestParser()
		parser.add_argument('price',
			type=float,
			required=True,
			help="This field cannot be left blank!"
		)
		request_data = parser.parse_args()

		if next(filter(lambda x: x['name'] == name, items), None):
			return {'message': 'An item with name {} already exists.'.format(name)}, 400
		else:
			item = {'name': name, 'price': request_data['price']}
			items.append(item)
			return {'item': item}
	
	@jwt_required()
	def delete(self, name):
		global items
		items = list(filter(lambda x: x['name'] != name, items))
		return {'message': 'Item deleted'}
		
	@jwt_required()
	def put(self, name):
		parser = reqparse.RequestParser()
		parser.add_argument('price',
			type=float,
			required=True,
			help="This field cannot be left blank!"
		)
		request_data = parser.parse_args()
		
		item = next(filter(lambda x: x['name'] == name, items), None)
		if item is None:
			item = {'name': name, 'price': request_data['price']}
			items.append(item)
		else:
			item.update(request_data)
		return item


class ItemList(Resource):
	@jwt_required()
	def get(self):
		return {'items': items}

api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')

app.run(port=5000, debug=True)
