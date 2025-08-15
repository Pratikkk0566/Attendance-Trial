from datetime import datetime, date
from bson import ObjectId
from flask import Blueprint, current_app, request, jsonify, abort
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from ..utils.security import role_required
from ..utils.storage import save_image
from ..services.face import get_face_encoding, compare_encodings

bp = Blueprint("attendance", __name__)


def _start_end_of_day(dt: datetime) -> tuple[datetime, datetime]:
	start = datetime(dt.year, dt.month, dt.day)
	end = datetime(dt.year, dt.month, dt.day, 23, 59, 59, 999999)
	return start, end


@bp.post("")
@role_required(["student"])
def submit_attendance():
	verify_jwt_in_request()
	user_id = get_jwt_identity()
	claims = get_jwt()
	student_id = ObjectId(user_id)
	company_id = claims.get("company_id")

	if "image" not in request.files:
		abort(400, description="image is required")
	try:
		lat = float(request.form.get("lat"))
		lon = float(request.form.get("lon"))
	except Exception:
		abort(400, description="lat and lon are required and must be numbers")

	db = current_app.db
	student = db.users.find_one({"_id": student_id})
	if not student:
		abort(404, description="student not found")

	# Enforce once per day
	now_utc = datetime.utcnow()
	start, end = _start_end_of_day(now_utc)
	existing = db.attendance_records.find_one({
		"student_id": str(student_id),
		"timestamp": {"$gte": start, "$lte": end},
	})
	if existing:
		return jsonify({"message": "Already marked today", "status": existing.get("status", "Present")}), 200

	image_file = request.files["image"]
	save_info = save_image(image_file)
	image_file.stream.seek(0)
	img_bytes = image_file.read()

	face_encoding = get_face_encoding(img_bytes)
	status = "Rejected"
	score = None
	reason = None
	if face_encoding and student.get("face_encoding"):
		ok, dist = compare_encodings(student["face_encoding"], face_encoding, tolerance=float(current_app.config.get("FACE_TOLERANCE", 0.6)))
		score = float(dist)
		status = "Present" if ok else "Rejected"
	else:
		reason = "Face template not available"

	record = {
		"student_id": str(student_id),
		"company_id": company_id,
		"timestamp": now_utc,
		"location": {"lat": lat, "lon": lon},
		"image": save_info,
		"status": status,
		"score": score,
		"reason": reason,
	}
	res = db.attendance_records.insert_one(record)
	return jsonify({"_id": str(res.inserted_id), "status": status, "score": score, "reason": reason}), 201


@bp.get("/me")
@role_required(["student"]) 
def my_records():
	verify_jwt_in_request()
	user_id = get_jwt_identity()
	db = current_app.db
	records = list(db.attendance_records.find({"student_id": str(ObjectId(user_id))}).sort("timestamp", -1).limit(200))
	for r in records:
		r["_id"] = str(r["_id"]) 
	return jsonify(records)