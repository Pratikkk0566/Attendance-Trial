## Attendance App (Flask + React + MongoDB Atlas)

Local development quickstart

Backend
- Python 3.11+
- In `backend/`:
  - Copy `.env.example` to `.env` and set `MONGO_URI`, `JWT_SECRET_KEY`
  - Install deps: `pip install -r requirements.txt`
  - Run: `python run.py`

Frontend
- Node 18+
- In `frontend/`:
  - `npm install`
  - `npm run dev`
- Vite dev server proxies `/api` to `http://localhost:5000`

Features
- JWT Auth for students and admins
- Student: selfie + geolocation attendance (once per day)
- Admin: filter by date/company/student, export to .xlsx
- Optional face recognition via `face_recognition` or `DeepFace` (install separately if needed)

Notes
- Images stored locally in `backend/uploads/` by default. Set `USE_GRIDFS=true` to store in MongoDB GridFS.
- Create seed users via UI at `/dev/register` (dev only) or `POST /api/auth/register`.