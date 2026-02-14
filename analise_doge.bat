@echo off
chcp 65001 >nul
echo ========================================
echo 📊 ANÁLISE - DOGECOIN
echo ========================================
echo.
echo Analisando DOGEUSDT...
echo Resultado será enviado para o Telegram
echo.
set PYTHONIOENCODING=utf-8
python analise_telegram.py doge
echo.
echo ========================================
pause
