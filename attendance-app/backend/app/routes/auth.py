from datetime import datetime
from bson import ObjectId
from flask import Blueprint, current_app, request, jsonify, abort
from flask_jwt_extended import create_access_token
from ..utils.security import hash_password, verify_password
from ..services.face import get_face_encoding

bp = Blueprint("auth", __name__)


@bp.post("/register")
def register():
	# Dev/seed endpoint: create user with optional face template
	data = request.form if request.form else request.json or {}
	username = (data.get("username") or "").strip().lower()
	password = data.get("password") or ""
	role = (data.get("role") or "student").strip().lower()
	company_id = data.get("company_id")
	full_name = data.get("full_name")
	if not username or not password:
		abort(400, description="username and password are required")
	if role not in {"student", "company_admin", "faculty_admin"}:
		abort(400, description="invalid role")

	db = current_app.db
	if db.users.find_one({"username": username}):
		abort(409, description="username already exists")

	face_encoding = None
	if "image" in request.files:
		image_file = request.files["image"]
		face_encoding = get_face_encoding(image_file.read())

	user_doc = {
		"username": username,
		"password_hash": hash_password(password),
		"role": role,
		"company_id": company_id,
		"face_encoding": face_encoding,
		"full_name": full_name,
		"created_at": datetime.utcnow(),
	}
	res = db.users.insert_one(user_doc)
	return jsonify({"_id": str(res.inserted_id), "username": username, "role": role}), 201


@bp.post("/login")
def login():
	data = request.json or {}
	username = (data.get("username") or "").strip().lower()
	password = data.get("password") or ""
	if not username or not password:
		abort(400, description="username and password are required")
	db = current_app.db
	user = db.users.find_one({"username": username})
	if not user or not verify_password(password, user.get("password_hash", "")):
		abort(401, description="invalid credentials")

	claims = {
		"role": user.get("role"),
		"username": user.get("username"),
		"company_id": user.get("company_id"),
	}
	token = create_access_token(identity=str(user["_id"]), additional_claims=claims)
	return jsonify({
		"access_token": token,
		"user": {
			"_id": str(user["_id"]),
			"username": user.get("username"),
			"role": user.get("role"),
			"company_id": user.get("company_id"),
			"full_name": user.get("full_name"),
		}
	})


@bp.get("/me")
def me():
	from flask_jwt_extended import get_jwt_identity, get_jwt, verify_jwt_in_request
	verify_jwt_in_request()
	user_id = get_jwt_identity()
	claims = get_jwt()
	db = current_app.db
	user = db.users.find_one({"_id": ObjectId(user_id)})
	if not user:
		abort(404, description="user not found")
	return jsonify({
		"_id": str(user["_id"]),
		"username": user.get("username"),
		"role": user.get("role"),
		"company_id": user.get("company_id"),
		"full_name": user.get("full_name"),
		"claims": claims,
	})