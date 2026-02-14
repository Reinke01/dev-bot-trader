@echo off
chcp 65001 >nul
echo ========================================
echo 📊 ANÁLISE - ETHEREUM
echo ========================================
echo.
echo Analisando ETHUSDT...
echo Resultado será enviado para o Telegram
echo.
set PYTHONIOENCODING=utf-8
python analise_telegram.py eth
echo.
echo ========================================
pause
