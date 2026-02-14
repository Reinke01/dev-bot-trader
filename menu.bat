@echo off
chcp 65001 >nul
:menu
cls
echo ========================================
echo     🤖 BOT TRADER - MENU PRINCIPAL
echo ========================================
echo.
echo  ROBÔS DISPONÍVEIS:
echo  [1] 🐕 DOGE - Dogecoin
echo  [2] ₿  BTC  - Bitcoin
echo  [3] ⚡ ETH  - Ethereum
echo  [4] 🌞 SOL  - Solana
echo.
echo  FERRAMENTAS:
echo  [5] 📊 Scanner de Oportunidades
echo  [6] 🌐 Scanner Web (API)
echo  [7] 🛑 Parar Todos os Robôs
echo.
echo  ANÁLISES (Telegram):
echo  [8] 📈 Analisar Bitcoin
echo  [9] 📈 Analisar Dogecoin
echo  [10] 📈 Analisar Ethereum
echo.
echo  [11] 📱 Testar Telegram
echo  [0] ❌ Sair
echo.
echo ========================================
set /p opcao="Digite a opção: "

if "%opcao%"=="1" (
    cls
    call start_doge.bat
    goto menu
)
if "%opcao%"=="2" (
    cls
    call start_btc.bat
    goto menu
)
if "%opcao%"=="3" (
    cls
    call start_eth.bat
    goto menu
)
if "%opcao%"=="4" (
    cls
    call start_sol.bat
    goto menu
)
if "%opcao%"=="5" (
    cls
    call scanner.bat
    goto menu
)
if "%opcao%"=="6" (
    cls
    call scanner_web.bat
    goto menu
)
if "%opcao%"=="7" (
    cls
    call stop_robots.bat
    goto menu
)
if "%opcao%"=="8" (
    cls
    call analise_btc.bat
    goto menu
)
if "%opcao%"=="9" (
    cls
    call analise_doge.bat
    goto menu
)
if "%opcao%"=="10" (
    cls
    call analise_eth.bat
    goto menu
)
if "%opcao%"=="11" (
    cls
    call test_telegram.bat
    goto menu
)
if "%opcao%"=="0" (
    echo.
    echo 👋 Até logo!
    timeout /t 2 >nul
    exit
)

echo.
echo ❌ Opção inválida! Tente novamente.
timeout /t 2 >nul
goto menu
