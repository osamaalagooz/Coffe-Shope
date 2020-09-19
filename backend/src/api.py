import json

from flask import Flask, request, jsonify, abort
from flask_cors import CORS

from .auth.auth import AuthError, requires_auth
from .database.models import db_drop_and_create_all, setup_db, Drink

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()


# ROUTES

@app.route('/drinks', methods=["GET"])
def get_drinks():
    try:
        all_drinks = Drink.query.all()

        drinks = [drink.short() for drink in all_drinks]

        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except:
        abort(404)


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    try:

        all_drinks = Drink.query.all()

        drinks = [drink.long() for drink in all_drinks]

        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except:
        abort(401)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def insert_drink(jwt):
    body = request.get_json()
    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)
    try:
        drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
        drink.insert()
        drink_new = Drink.query.all()
        drinks = [drink_added.long() for drink_added in drink_new]
        return jsonify({
            'success': True,
            'drinks': drinks

        })
    except:
        abort(401)


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink == None:
            abort(404)

        body = request.get_json()
        new_title = body.get('title', None)
        new_recipe = body.get('recipe', None)
        try:
            drink.title = new_title
            drink.recipe = json.dumps(new_recipe)
            drink.update()
            drink_new = Drink.query.all()
            drinks = [drink_added.long() for drink_added in drink_new]
            return jsonify({
                'success': True,
                'drinks': drinks

            })
        except:
            abort(400)
    except:
        abort(401)


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink == None:
            abort(404)

        drink.delete()

        return jsonify({
            'success': True,
            'delete': drink_id

        })
    except:
        abort(401)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not Found"
    }), 404


@app.errorhandler(401)
def not_authorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "not Authorized"
    }), 401


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Not Authorized"
    }), 401
