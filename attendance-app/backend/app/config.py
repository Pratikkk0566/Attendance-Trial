import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load .env if present
load_dotenv()


@dataclass
class Config:
	MONGO_URI: str = os.environ.get("MONGO_URI", "")
	MONGO_DB_NAME: str | None = os.environ.get("MONGO_DB_NAME")
	JWT_SECRET_KEY: str | None = os.environ.get("JWT_SECRET_KEY")
	CORS_ORIGINS: str = os.environ.get("CORS_ORIGINS", "*")
	UPLOAD_FOLDER: str | None = os.environ.get("UPLOAD_FOLDER")
	USE_GRIDFS: str | None = os.environ.get("USE_GRIDFS")
	FACE_TOLERANCE: float = float(os.environ.get("FACE_TOLERANCE", "0.6"))