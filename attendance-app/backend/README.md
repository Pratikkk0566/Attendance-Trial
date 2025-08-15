### Backend (Flask) - Attendance App

Requirements:
- Python 3.11+ (works with 3.13 too)
- MongoDB Atlas connection string

Setup:
1. Create and fill `.env` from `.env.example`.
2. (Optional) Create a venv and activate it.
3. Install requirements:
```
pip install -r requirements.txt
```
4. Run in development:
```
python run.py
```

APIs:
- `POST /api/auth/register` (dev only): form-data: username, password, role, company_id, full_name, image(optional)
- `POST /api/auth/login` JSON: { username, password }
- `GET /api/auth/me`
- `POST /api/attendance` form-data (JWT required, role student): image(file), lat, lon
- `GET /api/attendance/me` (JWT required, role student)
- `GET /api/admin/records?company=...&student=...&start=YYYY-MM-DD&end=YYYY-MM-DD` (JWT required, company_admin/faculty_admin)
- `GET /api/admin/export?...same filters...` -> .xlsx

Notes:
- Face recognition uses optional libraries. If not installed, attendance will be saved with status based on availability of face templates.
- For production, enable GridFS by setting `USE_GRIDFS=true`.