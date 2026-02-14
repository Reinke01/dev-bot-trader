@echo off
chcp 65001 >nul
echo ========================================
echo 🇧🇷 DIDI INDEX - BITCOIN
echo ========================================
echo.
echo Detectando Agulhadas e Puntos...
echo Indicador Brasileiro de Reversão
echo.
set PYTHONIOENCODING=utf-8
python analise_didi_index.py btc
echo.
echo ========================================
pause
