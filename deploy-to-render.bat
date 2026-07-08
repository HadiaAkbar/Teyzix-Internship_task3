@echo off
REM Render.com Backend Deployment Script for Contract Analyzer (Windows)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  Contract Analyzer - Backend Deployment to Render.com     ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Get current git remote URL
for /f "tokens=*" %%i in ('git remote get-url origin') do set REMOTE_URL=%%i

if "%REMOTE_URL%"=="" (
    echo ❌ Not a git repository or git is not installed
    pause
    exit /b 1
)

echo 📦 Repository: %REMOTE_URL%
echo.

echo 📝 Next Steps to Deploy on Render.com:
echo.
echo 1. Go to https://render.com and sign up ^(free tier available^)
echo.
echo 2. Click 'New +' -^> 'Web Service'
echo.
echo 3. Configure with these settings:
echo    ├─ Repository: https://github.com/HadiaAkbar/Contract-Risk-analyzer
echo    ├─ Root Directory: contract-analyzer
echo    ├─ Build Command: pip install -r requirements.txt
echo    ├─ Start Command: uvicorn app.main:app --host 0.0.0.0 --port 8000
echo    ├─ Environment: Python 3.11
echo    └─ Plan: Free
echo.
echo 4. Click 'Create Web Service'
echo.
echo 5. Wait for deployment to complete (~3-5 minutes^)
echo.
echo 6. Copy your service URL ^(e.g., https://contract-analyzer-api.render.com^)
echo.
echo 7. Update Streamlit Secrets:
echo    ├─ Go to https://share.streamlit.io/
echo    ├─ Select your app -^> App settings -^> Secrets
echo    ├─ Add: API_URL = "https://your-render-service.render.com"
echo    └─ Click 'Save'
echo.
echo 8. ✅ Your app should now work!
echo.
echo 📚 For detailed instructions, see: DEPLOYMENT.md
echo.
pause
