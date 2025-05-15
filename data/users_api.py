from flask import Blueprint, jsonify, make_response, request
from datetime import datetime

from . import db_session
from .users import User


users_api = Blueprint("users_api",
                     __name__,
                     template_folder="templates")


@users_api.route("/api/users/")
def get_users():
    db_sess = db_session.create_session()

    users = db_sess.query(User).all()

    return jsonify({"users": [user.to_dict() for user in users]})


@users_api.route("/api/users/<int:user_id>")
def get_user(user_id):
    db_sess = db_session.create_session()

    user = db_sess.query(User).get(user_id)

    if not user:
        return make_response(jsonify({'error': 'Not found'}), 404)

    return jsonify({"users": [user.to_dict()]})


@users_api.route("/api/users/", methods=["POST"])
def create_user():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    
    allowed_fields = ["id", "surname", "name", "age", "position", "speciality", "address", "email", "hashed_password", "modified_date"] 

    if not all(key in request.json for key in allowed_fields):
        return make_response(jsonify({'error': 'Missing fields'}), 400)

    db_sess = db_session.create_session()

    password_hash = request.json["hashed_password"]

    hash_method = password_hash.split("$")[0]

    if ":".join(hash_method.split(':')[:2]) != "pbkdf2:sha256":
        return make_response(jsonify({'error': 'Wrong type hash. Must be werkzeug type.'}), 404)

    modified_date = request.json["modified_date"]

    if modified_date:
        modified_date = datetime.fromisoformat(modified_date)

    user = User(
        id=request.json["id"],
        surname=request.json["surname"],
        name=request.json["name"],
        age=request.json["age"],
        position=request.json["position"],
        speciality=request.json["speciality"],
        address=request.json["address"],
        email=request.json["email"],
        hashed_password=password_hash,
        modified_date=modified_date,
    )

    if db_sess.query(User).filter(User.id == user.id).first():
        return make_response(jsonify({'error': 'Id already exists'}), 400)

    db_sess.add(user)
    db_sess.commit()

    return jsonify({'success': 'OK'})


@users_api.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    db_sess = db_session.create_session()

    user = db_sess.query(User).get(user_id)

    if not user:
        return make_response(jsonify({'error': 'Not found'}), 400)

    db_sess.delete(user)
    db_sess.commit()

    return jsonify({'success': 'OK'})


@users_api.route("/api/users/<int:user_id>", methods=["PUT"])
def edit_user(user_id):
    db_sess = db_session.create_session()

    user = db_sess.query(User).get(user_id)

    if not user:
        return make_response(jsonify({'error': 'Not found'}), 404)

    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)

    allowed_fields = ["id", "surname", "name", "age", "position", "speciality", "address", "email", "hashed_password", "modified_date"]

    if not all(key in request.json for key in allowed_fields):
        return make_response(jsonify({'error': 'Missing fields'}), 400)

    password_hash = request.json["hashed_password"]

    hash_method = password_hash.split("$")[0]

    if ":".join(hash_method.split(':')[:2]) != "pbkdf2:sha256":
        return make_response(jsonify({'error': 'Wrong type hash. Must be werkzeug type.'}), 404)

    modified_date = request.json["modified_date"]

    if modified_date:
        modified_date = datetime.fromisoformat(modified_date)

    user.id = request.json["id"]
    user.surname = request.json["surname"]
    user.name = request.json["name"]
    user.age = request.json["age"]
    user.position = request.json["position"]
    user.speciality = request.json["speciality"]
    user.address = request.json["address"]
    user.email = request.json["email"]
    user.hashed_password = password_hash
    user.modified_date = modified_date

    db_sess.commit()

    return jsonify({'success': 'OK'})