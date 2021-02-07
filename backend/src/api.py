import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/', methods= ['GET'])
def rooty():
    return jsonify({
        'success': True,
        'message': 'Happy testing'
    })

@app.route('/drinks', methods= ['GET'])
def get_drinks():
    drinks_all = Drink.query.all()
    if len(drinks_all) == 0:
        abort(404)
    drinks = [drink.short() for drink in drinks_all]
    return jsonify({
        "success": True,
        "drinks": drinks
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods= ['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks_all = Drink.query.all()
    if len(drinks_all) == 0:
        abort(404)
    drinks = [drink.long() for drink in drinks_all]
    return jsonify({
        "success": True,
        "drinks": drinks
    })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(payload):
    data = request.get_json()

    drink_title = data['title']
    drink_recipe = json.dumps(data['recipe'])

    if drink_title is None or drink_recipe is None:
        abort(422)

    try:
        new_drink = Drink(title=drink_title, recipe=drink_recipe)
        new_drink.insert()

        return jsonify({
            'success': True,
            'drinks': [new_drink.long()]
        }), 200

    except:
        abort(500)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(payload, id):
    data = request.get_json()

    #drink = Drink.query.get(id)
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)

    try:
        if 'title' in data:
            drink.title = data['title']

        if 'recipe' in data:
            drink.recipe = data['recipe']

        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200

    except:
        abort(500)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink_by_id(payload, id):
    drink = Drink.query.filter(Drink.id==id).one_or_none()
    if drink is None:
        abort(404)
    else:
        drink.delete()
    return jsonify({
        'success': True,
        "delete": id
    })



## Error Handling
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

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request. Check request body"
    }), 400


'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
        }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''

@app.errorhandler(AuthError)
def authError(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        #"message": error.error['description']
        "message": error.error
    }), error.status_code