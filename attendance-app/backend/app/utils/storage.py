import os
import uuid
from typing import Any, Dict, Tuple
from werkzeug.datastructures import FileStorage
from flask import current_app


def save_image(file_storage: FileStorage) -> Dict[str, Any]:
	use_gridfs = getattr(current_app, "use_gridfs", False)
	if use_gridfs and getattr(current_app, "gridfs", None) is not None:
		grid = current_app.gridfs
		file_id = grid.put(file_storage.stream, filename=file_storage.filename or f"img_{uuid.uuid4().hex}.jpg")
		return {"gridfs_id": str(file_id), "storage": "gridfs"}
	else:
		upload_folder = getattr(current_app, "upload_folder")
		os.makedirs(upload_folder, exist_ok=True)
		ext = os.path.splitext(file_storage.filename or "image.jpg")[1]
		filename = f"{uuid.uuid4().hex}{ext if ext else '.jpg'}"
		path = os.path.join(upload_folder, filename)
		file_storage.save(path)
		return {"path": path, "filename": filename, "storage": "local"}