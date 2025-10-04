from flask import Blueprint, jsonify

bp = Blueprint('example', __name__)

@bp.route('/hello')
def hello():
    return jsonify({"message": "Hello from Flask!"})