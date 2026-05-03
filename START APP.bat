@echo off
title RAG-SQL-Python-Assistant Launcher
echo.
echo  =====================================================
echo    RAG-SQL-Python-Assistant - One Click Launcher
echo  =====================================================
echo.
echo  Starting all services... Please wait...
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1"
pause
