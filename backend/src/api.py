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

"""
#@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
"""
# db_drop_and_create_all()

## ROUTES
"""
#@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks")
def get_drinks():
    """
    Get the drinks in the menu with short description.
    """
    all_drinks = Drink.query.all()
    if len(all_drinks) == 0:
        abort(404)
    drinks_short_formatted = [drink.short() for drink in all_drinks]
    return jsonify({"success": True, "drinks": drinks_short_formatted})


"""
#@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks-detail")
@requires_auth("get:drinks-detail")
def get_drink_details(payload):
    """
    Get the drinks in the menu with long description.
    """
    all_drinks = Drink.query.all()
    if len(all_drinks) == 0:
        abort(404)
    drinks_long_formatted = [drink.long() for drink in all_drinks]
    return jsonify({"success": True, "drinks": drinks_long_formatted})


"""
#@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def post_drink(payload):
    """
    Post a drink.
    """
    body = request.get_json()
    title = body.get("title", None)
    recipe = json.dumps(body.get("recipe", None))
    # There is missing data so i am going to abort
    if not title or not recipe:
        abort(422)

    drink = Drink.query.filter(Drink.title == title).one_or_none()
    # There is a drink with this title so I have to abort
    if drink:
        abort(409)
    try:
        drink = Drink(title=title, recipe=recipe)
        drink.insert()
        return jsonify({"success": True, "drinks": drink.long()})
    except:
        abort(422)


"""
#@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks/<int:id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def patch_drinks_details(payload, id):
    """
    Update drink details.
    """
    try:
        body = request.get_json()
        title = body.get("title", None)
        recipe = json.dumps(body.get("recipe", None))
        # If there is no title and no recipe then abort
        if not title and not recipe:
            abort(422)
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if not drink:
            abort(400)
        if title:
            drink.title = title
        if recipe and recipe != "null":
            drink.recipe = recipe
        drink.update()
        return jsonify({"success": True, "drinks": [drink.long()]})
    except:
        abort(422)


"""
#@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks/<int:id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drinks(payload, id):
    """
    Delete a drink.
    """
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if not drink:
            abort(400)
        drink.delete()
        return {"success": True, "delete": id}
    except:
        abort(422)


## Error Handling
"""
Example error handling for unprocessable entity
"""


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({"success": False, "error": 422, "message": "unprocessable"}), 422


@app.errorhandler(404)
def not_found(error):
    return (
        jsonify({"success": False, "error": 404, "message": "resource not found"}),
        404,
    )


@app.errorhandler(400)
def bad_request(error):
    return (
        jsonify({"success": False, "error": 400, "message": "bad request"}),
        400,
    )


@app.errorhandler(405)
def not_allowed(error):
    return (
        jsonify({"success": False, "error": 405, "message": "not allowed"}),
        405,
    )


@app.errorhandler(409)
def conflict(error):
    return (
        jsonify(
            {
                "success": False,
                "error": 409,
                "message": "conflicts with some rule already established",
            }
        ),
        409,
    )


@app.errorhandler(401)
def unauthorized(error):
    return (
        jsonify({"success": False, "error": 401, "message": "not authorized",}),
        401,
    )


@app.errorhandler(403)
def forbidden(error):
    return (
        jsonify({"success": False, "error": 403, "message": "forbidden",}),
        403,
    )


@app.errorhandler(AuthError)
def authorize_authenticate_error(error):
    return (
        jsonify({"success": False, "error": error.status_code, "message": error.error}),
        error.status_code,
    )


"""
#@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

"""

"""
#@TODO implement error handler for 404
    error handler should conform to general task above 
"""


"""
#@TODO implement error handler for AuthError
    error handler should conform to general task above 
"""
