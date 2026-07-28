@echo off
setlocal
cd /d "%~dp0"

if not exist "server\venv\Scripts\python.exe" (
  echo Backend environment is missing.
  echo Run: cd server ^&^& python -m venv venv ^&^& venv\Scripts\pip install -r requirements.txt
  pause
  exit /b 1
)

if not exist "client\node_modules" (
  echo Frontend dependencies are missing.
  echo Run: cd client ^&^& npm install
  pause
  exit /b 1
)

start "Ayett Stories Backend" cmd /k "cd /d %~dp0server && venv\Scripts\python -m uvicorn api:app --reload --port 8000"
start "Ayett Stories Frontend" cmd /k "cd /d %~dp0client && npm run dev"

echo Ayett Stories is starting at http://localhost:3000
endlocal
