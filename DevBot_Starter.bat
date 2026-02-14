@echo off
title Dev Bot Trader - Launcher
echo ==========================================
echo       DEV BOT TRADER - INITIALIZING
echo ==========================================
echo.

echo [1/3] Iniciando Servidor API (Backend)...
start "DevBot Backend" cmd /k "cd src && uvicorn api.main:app --host 0.0.0.0 --port 8000"

echo [2/3] Iniciando Terminal Monitor (Frontend)...
start "DevBot Frontend" cmd /k "cd src/monitor_web && npm run dev"

echo [3/3] Criando link de acesso externo...
echo.
echo ------------------------------------------
echo AGUARDE O LINK APARECER ABAIXO...
echo Quando o link aparecer, envie para seu amigo.
echo Se pedir senha, use o IP que aparecer no seu navegador.
echo ------------------------------------------
echo.
npx localtunnel --port 5173

pause
