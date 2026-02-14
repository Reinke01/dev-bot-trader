@echo off
chcp 65001 >nul
echo ========================================
echo 🐕 INICIANDO ROBÔ - DOGECOIN
echo ========================================
echo.
echo Moeda: DOGEUSDT
echo Estratégia: Double EMA Breakout + IA
echo Modo: Simulação
echo.
echo Pressione CTRL+C para parar o robô
echo ========================================
echo.
set PYTHONIOENCODING=utf-8
set PYTHONPATH=backend/src
python backend/src/live_trading/double_ema_breakout_orders_long_short_dual_params_agent_evaluator.py --cripto DOGEUSDT --is_simulator
pause
