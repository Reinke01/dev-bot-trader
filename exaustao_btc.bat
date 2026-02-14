@echo off
chcp 65001 >nul
echo ========================================
echo 🔍 ANÁLISE DE EXAUSTÃO - BITCOIN
echo ========================================
echo.
echo Detectando sinais de reversão...
echo.
set PYTHONIOENCODING=utf-8
python analise_exaustao.py btc
echo.
echo ========================================
pause
