@echo off
echo ========================================================
echo   PageTurner Online Bookstore - Quick Frontend Preview
echo ========================================================
echo.
echo Starting local web server for static frontend...
cd src\main\resources\static
start http://localhost:8080
python -m http.server 8080
pause
