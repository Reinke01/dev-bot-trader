@echo off
chcp 65001 >nul
:menu
cls
echo ========================================
echo   💎 BOT TRADER - MENU PROFISSIONAL
echo ========================================
echo.
echo  🤖 ROBÔS (Score Atual):
echo  [1]  🥇 ARB  - Arbitrum (42/100)
echo  [2]  🐕 DOGE - Dogecoin (28.9/100) - ATIVO
echo  [3]  ₿  BTC  - Bitcoin (28.4/100)
echo  [4]  ⚡ ETH  - Ethereum (26.5/100)
echo  [5]  🌞 SOL  - Solana (31.1/100)
echo  [6]  💎 ADA  - Cardano (25.1/100)
echo  [7]  🔺 AVAX - Avalanche (27.7/100)
echo.
echo  📊 ANÁLISE PROFISSIONAL (0-100):
echo  [10] 🔍 Varredura Profissional
echo  [11] 💎 Dashboard Visual (Navegador)
echo  [12] 🇧🇷 Didi + Bollinger (BTC)
echo  [13] 🎯 Análise Reversão Avançada (BTC)
echo.
echo  📈 SCANNER:
echo  [15] 📊 Scanner Simples
echo  [16] 🌐 Scanner Web
echo.
echo  🔍 ANÁLISES RÁPIDAS (Telegram):
echo  [20] BTC  [21] ETH   [22] DOGE
echo  [23] SOL  [24] AVAX  [25] ARB
echo.
echo  🛠️ UTILITÁRIOS:
echo  [30] 🛑 Parar Todos os Robôs
echo  [31] 📱 Testar Telegram
echo  [32] 📋 Ver Guia Completo
echo.
echo  [0] ❌ Sair
echo.
echo ========================================
set /p opcao="💡 Digite a opção: "

if "%opcao%"=="1" (
    cls
    call start_arb.bat
    goto menu
)
if "%opcao%"=="2" (
    cls
    call start_doge.bat
    goto menu
)
if "%opcao%"=="3" (
    cls
    call start_btc.bat
    goto menu
)
if "%opcao%"=="4" (
    cls
    call start_eth.bat
    goto menu
)
if "%opcao%"=="5" (
    cls
    call start_sol.bat
    goto menu
)
if "%opcao%"=="6" (
    cls
    call start_ada.bat
    goto menu
)
if "%opcao%"=="7" (
    cls
    call start_avax.bat
    goto menu
)

if "%opcao%"=="10" (
    cls
    call varredura_pro.bat
    goto menu
)
if "%opcao%"=="11" (
    cls
    echo.
    echo ========================================
    echo 💎 Abrindo Dashboard Profissional...
    echo ========================================
    echo.
    start dashboard_profissional.html
    timeout /t 2 >nul
    goto menu
)
if "%opcao%"=="12" (
    cls
    call didi_bb_btc.bat
    goto menu
)
if "%opcao%"=="13" (
    cls
    call reversao_btc.bat
    goto menu
)

if "%opcao%"=="15" (
    cls
    call scanner.bat
    goto menu
)
if "%opcao%"=="16" (
    cls
    call scanner_web.bat
    goto menu
)

if "%opcao%"=="20" (
    cls
    call analise_btc.bat
    goto menu
)
if "%opcao%"=="21" (
    cls
    call analise_eth.bat
    goto menu
)
if "%opcao%"=="22" (
    cls
    call analise_doge.bat
    goto menu
)
if "%opcao%"=="23" (
    cls
    echo.
    echo Analisando SOL...
    set PYTHONIOENCODING=utf-8
    python analise_telegram.py sol
    pause
    goto menu
)
if "%opcao%"=="24" (
    cls
    echo.
    echo Analisando AVAX...
    set PYTHONIOENCODING=utf-8
    python analise_telegram.py avax
    pause
    goto menu
)
if "%opcao%"=="25" (
    cls
    echo.
    echo Analisando ARB...
    set PYTHONIOENCODING=utf-8
    python analise_telegram.py arb
    pause
    goto menu
)

if "%opcao%"=="30" (
    cls
    call stop_robots.bat
    goto menu
)
if "%opcao%"=="31" (
    cls
    call test_telegram.bat
    goto menu
)
if "%opcao%"=="32" (
    cls
    echo.
    type GUIA_SISTEMA_PROFISSIONAL.txt
    echo.
    pause
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
