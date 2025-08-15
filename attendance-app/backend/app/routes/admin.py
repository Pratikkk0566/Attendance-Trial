from datetime import datetime
from io import BytesIO
from bson import ObjectId
from flask import Blueprint, current_app, request, jsonify, abort, send_file
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from ..utils.security import role_required
from openpyxl import Workbook

bp = Blueprint("admin", __name__)


def _build_filters(args, is_company_admin: bool, admin_company_id: str | None):
	filters = {}
	company = args.get("company")
	start = args.get("start")
	end = args.get("end")
	if is_company_admin:
		filters["company_id"] = admin_company_id
	elif company:
		filters["company_id"] = company
	# time range
	if start or end:
		filters["timestamp"] = {}
		if start:
			filters["timestamp"]["$gte"] = datetime.fromisoformat(start)
		if end:
			filters["timestamp"]["$lte"] = datetime.fromisoformat(end)
	return filters


def _resolve_student_ids(db, student_query: str | None):
	if not student_query:
		return None
	# Match by username or full_name (case-insensitive contains)
	regex = {"$regex": student_query, "$options": "i"}
	users = list(db.users.find({"$or": [{"username": regex}, {"full_name": regex}]}).limit(500))
	return [str(u["_id"]) for u in users]


def _get_pagination(args):
	try:
		page = max(1, int(args.get("page", 1)))
		limit = min(1000, max(1, int(args.get("limit", 50))))
	except Exception:
		page, limit = 1, 50
	skips = (page - 1) * limit
	return page, limit, skips


@bp.get("/records")
@role_required(["company_admin", "faculty_admin"]) 
def list_records():
	verify_jwt_in_request()
	claims = get_jwt()
	is_company_admin = claims.get("role") == "company_admin"
	admin_company_id = claims.get("company_id")

	db = current_app.db
	filters = _build_filters(request.args, is_company_admin, admin_company_id)
	student_query = request.args.get("student")
	student_ids = _resolve_student_ids(db, student_query)
	if student_ids is not None:
		filters["student_id"] = {"$in": student_ids}

	page, limit, skips = _get_pagination(request.args)

	# Join user info (denormalized with username)
	total = db.attendance_records.count_documents(filters)
	records = list(db.attendance_records.find(filters).sort("timestamp", -1).skip(skips).limit(limit))
	user_ids = {r.get("student_id") for r in records}
	obj_ids = [ObjectId(uid) for uid in user_ids if uid]
	user_map = {str(u["_id"]): u for u in db.users.find({"_id": {"$in": obj_ids}})} if obj_ids else {}
	for r in records:
		u = user_map.get(r.get("student_id"))
		r["_id"] = str(r["_id"]) 
		if u:
			r["student_username"] = u.get("username")
			r["student_full_name"] = u.get("full_name")
	return jsonify({"data": records, "page": page, "limit": limit, "total": total})


@bp.get("/export")
@role_required(["company_admin", "faculty_admin"]) 
def export_excel():
	verify_jwt_in_request()
	claims = get_jwt()
	is_company_admin = claims.get("role") == "company_admin"
	admin_company_id = claims.get("company_id")

	db = current_app.db
	filters = _build_filters(request.args, is_company_admin, admin_company_id)
	student_query = request.args.get("student")
	student_ids = _resolve_student_ids(db, student_query)
	if student_ids is not None:
		filters["student_id"] = {"$in": student_ids}

	records = list(db.attendance_records.find(filters).sort("timestamp", -1).limit(5000))
	user_ids = {r.get("student_id") for r in records}
	obj_ids = [ObjectId(uid) for uid in user_ids if uid]
	user_map = {str(u["_id"]): u for u in db.users.find({"_id": {"$in": obj_ids}})} if obj_ids else {}

	wb = Workbook()
	ws = wb.active
	ws.title = "Attendance"
	headers = ["Timestamp", "Company", "Student Username", "Student Name", "Latitude", "Longitude", "Status", "Score"]
	ws.append(headers)
	for r in records:
		u = user_map.get(r.get("student_id"))
		row = [
			r.get("timestamp"),
			r.get("company_id"),
			u.get("username") if u else None,
			u.get("full_name") if u else None,
			r.get("location", {}).get("lat"),
			r.get("location", {}).get("lon"),
			r.get("status"),
			r.get("score"),
		]
		ws.append(row)

	bio = BytesIO()
	wb.save(bio)
	bio.seek(0)
	return send_file(bio, as_attachment=True, download_name="attendance_export.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")