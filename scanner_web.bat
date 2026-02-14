@echo off
chcp 65001 >nul
echo ========================================
echo 🌐 SCANNER WEB - INICIANDO API
echo ========================================
echo.
echo API rodando em: http://localhost:8000
echo.
echo Para visualizar, abra: scanner_view.html
echo.
echo Pressione CTRL+C para parar
echo ========================================
echo.
set PYTHONPATH=%~dp0backend\src
python backend\src\start_api_scanner.py
pause
