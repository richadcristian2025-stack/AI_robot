@echo off
cls
echo ============================================================
echo    VOICE CONTROLLED ROBOT AI SYSTEM
echo ============================================================
echo.
echo Components:
echo   - ML AI Model (ml_ai.py)
echo   - Web Server (web_interface.py)
echo   - Arduino Firmware (robot.ino)
echo.
echo ============================================================
echo.
echo Starting web server on PORT 4141...
echo.
echo Access the interface at:
echo   http://localhost:4141
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

python web_interface.py

echo.
echo Server stopped.
pause
