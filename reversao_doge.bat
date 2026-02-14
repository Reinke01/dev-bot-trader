@echo off
chcp 65001 >nul
echo ========================================
echo 🔍 ANÁLISE AVANÇADA DE REVERSÃO - DOGE
echo ========================================
echo.
echo Indicadores: RSI, Stoch RSI, MFI, Williams %%R
echo             MACD, VWAP, Volume, Bollinger
echo.
set PYTHONIOENCODING=utf-8
python analise_reversao_avancada.py doge
echo.
echo ========================================
pause
