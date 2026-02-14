@echo off
chcp 65001 >nul
echo ========================================
echo 📊 VARREDURA + ANÁLISE BTC
echo ========================================
echo.
echo Analisando mercado e Bitcoin...
echo Enviando para Telegram...
echo.
set PYTHONIOENCODING=utf-8
python analise_completa_telegram.py btc
echo.
echo ========================================
pause
