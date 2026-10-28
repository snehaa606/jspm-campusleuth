@echo off
title JSPM CampuSleuth - Campus Lost and Found Engine
cd /d "%~dp0"
cls
echo =====================================================================
echo   JSPM University: CampuSleuth (AI Lost & Found Zero-Typing Hub)
echo =====================================================================
echo.
echo Starting Python Web Server...
echo DO NOT CLOSE this black window while testing the website!
echo.
python app.py
echo.
echo Server stopped.
pause
