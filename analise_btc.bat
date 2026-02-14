@echo off
chcp 65001 >nul
echo ========================================
echo 📊 ANÁLISE - BITCOIN
echo ========================================
echo.
echo Analisando BTCUSDT...
echo Resultado será enviado para o Telegram
echo.
set PYTHONIOENCODING=utf-8
python analise_telegram.py btc
echo.
echo ========================================
pause
