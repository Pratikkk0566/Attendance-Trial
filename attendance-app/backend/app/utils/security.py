from functools import wraps
from typing import Callable, Iterable
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from flask import abort
import bcrypt


def hash_password(plain_password: str) -> str:
	password_bytes = plain_password.encode("utf-8")
	salt = bcrypt.gensalt(rounds=12)
	return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
	try:
		return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
	except Exception:
		return False


def role_required(roles: Iterable[str]) -> Callable:
	roles_set = set(roles)

	def decorator(fn: Callable) -> Callable:
		@wraps(fn)
		def wrapper(*args, **kwargs):
			verify_jwt_in_request()
			claims = get_jwt()
			user_role = claims.get("role")
			if user_role not in roles_set:
				abort(403, description="Insufficient permissions")
			return fn(*args, **kwargs)
		return wrapper

	return decorator