@echo off
chcp 65001 >nul
echo ========================================
echo 📱 TESTE - TELEGRAM
echo ========================================
echo.
echo Enviando mensagem de teste...
echo.
set PYTHONIOENCODING=utf-8
python test_telegram.py
echo.
echo ========================================
pause
