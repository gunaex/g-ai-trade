@echo off
REM JWT Authentication Setup Script for Windows
REM Run this after pulling JWT authentication changes

echo =====================================
echo G-AI-TRADE JWT Authentication Setup
echo =====================================
echo.

echo [1/4] Installing Python dependencies...
pip install python-jose[cryptography]==3.3.0 passlib[bcrypt]==1.7.4 python-multipart==0.0.6
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed successfully
echo.

echo [2/4] Generating JWT secret key...
for /f "delims=" %%i in ('python -c "import secrets; print(secrets.token_urlsafe(32))"') do set JWT_SECRET=%%i
echo JWT_SECRET_KEY=%JWT_SECRET%
echo.
echo ⚠️  IMPORTANT: Add this to your .env file:
echo JWT_SECRET_KEY=%JWT_SECRET%
echo.

echo [3/4] Checking .env file...
if exist .env (
    echo ✓ .env file exists
    findstr /C:"JWT_SECRET_KEY" .env >nul
    if errorlevel 1 (
        echo ⚠️  JWT_SECRET_KEY not found in .env
        echo Adding JWT_SECRET_KEY to .env...
        echo. >> .env
        echo # JWT Authentication >> .env
        echo JWT_SECRET_KEY=%JWT_SECRET% >> .env
        echo ✓ JWT_SECRET_KEY added to .env
    ) else (
        echo ⚠️  JWT_SECRET_KEY already exists in .env
        echo Please verify it's set to a secure value
    )
) else (
    echo Creating .env from .env.example...
    copy .env.example .env
    echo. >> .env
    echo # JWT Authentication >> .env
    echo JWT_SECRET_KEY=%JWT_SECRET% >> .env
    echo ✓ .env created with JWT_SECRET_KEY
)
echo.

echo [4/4] Verifying installation...
python -c "from jose import jwt; from passlib.context import CryptContext; print('✓ All imports successful')" 2>nul
if errorlevel 1 (
    echo ❌ Import verification failed
    echo Please check your Python environment
    pause
    exit /b 1
)
echo ✓ Installation verified successfully
echo.

echo =====================================
echo Setup Complete!
echo =====================================
echo.
echo Next steps:
echo 1. Review your .env file and ensure JWT_SECRET_KEY is set
echo 2. Start the backend server: uvicorn app.main:app --reload
echo 3. Create your first user: POST /api/auth/register
echo 4. Test authentication: POST /api/auth/login
echo.
echo For more information, see:
echo - JWT_AUTHENTICATION.md
echo - JWT_IMPLEMENTATION_SUMMARY.md
echo - SECURITY.md
echo.
pause
