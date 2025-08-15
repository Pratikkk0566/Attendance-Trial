import os
from datetime import timedelta
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
import gridfs
from .config import Config

jwt = JWTManager()


def create_indexes(db):
	# Users
	try:
		db.users.create_index("username", unique=True)
		db.users.create_index("company_id")
		# Attendance indexes
		db.attendance_records.create_index("student_id")
		db.attendance_records.create_index("company_id")
		db.attendance_records.create_index("timestamp")
		db.attendance_records.create_index([("company_id", 1), ("timestamp", -1)])
	except Exception as exc:
		print(f"[WARN] Failed to create indexes: {exc}")


def create_app() -> Flask:
	app = Flask(__name__)
	app.config.from_object(Config())

	# CORS
	CORS(app, resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", "*")}}, supports_credentials=True)

	# JWT
	app.config["JWT_SECRET_KEY"] = app.config.get("JWT_SECRET_KEY") or os.environ.get("JWT_SECRET_KEY", "change-me")
	app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=12)
	jwt.init_app(app)

	# Mongo
	mongo_uri = app.config.get("MONGO_URI")
	if not mongo_uri:
		raise RuntimeError("MONGO_URI is not configured. Set it in environment or .env file.")
	client = MongoClient(mongo_uri, tlsAllowInvalidCertificates=bool(int(os.environ.get("MONGO_TLS_ALLOW_INVALID", "0"))))
	db_name = app.config.get("MONGO_DB_NAME")
	if not db_name:
		# Try to parse from URI path or default
		try:
			db_name = MongoClient(mongo_uri).get_default_database().name  # type: ignore
		except Exception:
			db_name = os.environ.get("MONGO_DB_NAME", "attendance_db")
	app.mongo_client = client  # type: ignore[attr-defined]
	app.db = client[db_name]  # type: ignore[attr-defined]

	# GridFS optional
	app.use_gridfs = str(app.config.get("USE_GRIDFS", "false")).lower() in ("1", "true", "yes")  # type: ignore[attr-defined]
	app.gridfs = gridfs.GridFS(app.db) if app.use_gridfs else None  # type: ignore[attr-defined]

	# Uploads
	upload_folder = app.config.get("UPLOAD_FOLDER") or os.path.join(os.getcwd(), "uploads")
	os.makedirs(upload_folder, exist_ok=True)
	app.upload_folder = upload_folder  # type: ignore[attr-defined]

	# Indexes
	create_indexes(app.db)

	# Register blueprints
	from .routes.auth import bp as auth_bp
	from .routes.attendance import bp as attendance_bp
	from .routes.admin import bp as admin_bp
	app.register_blueprint(auth_bp, url_prefix="/api/auth")
	app.register_blueprint(attendance_bp, url_prefix="/api/attendance")
	app.register_blueprint(admin_bp, url_prefix="/api/admin")

	@app.get("/api/health")
	def health():
		return {"status": "ok"}, 200

	return app