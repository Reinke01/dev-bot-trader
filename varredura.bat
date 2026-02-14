@echo off
chcp 65001 >nul
echo ========================================
echo 🔍 VARREDURA DIDI + BOLLINGER
echo ========================================
echo.
echo Analisando 20 principais moedas...
echo Buscando os melhores setups!
echo.
echo Aguarde 1-2 minutos...
echo.
set PYTHONPATH=%~dp0backend\src
python backend\src\varredura_didi_bollinger.py
echo.
echo ========================================
pause
