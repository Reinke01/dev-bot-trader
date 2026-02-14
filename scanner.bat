@echo off
chcp 65001 >nul
echo ========================================
echo 📊 SCANNER DE OPORTUNIDADES
echo ========================================
echo.
echo Analisando top 30 moedas...
echo.
set PYTHONIOENCODING=utf-8
python scanner_simple.py
echo.
echo ========================================
pause
