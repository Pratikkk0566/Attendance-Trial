@echo off
echo Starting Attendance App Development Environment...
echo.

echo [1/3] Starting Backend Server...
cd backend
start cmd /k "venv\Scripts\activate && python app.py"

echo [2/3] Starting Frontend Server...
cd ..\frontend
start cmd /k "npm start"

echo [3/3] Opening Browser...
timeout /t 5 /nobreak > nul
start http://localhost:3000

echo.
echo ✅ Development environment started!
echo.
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Press any key to close this window...
pause > nul