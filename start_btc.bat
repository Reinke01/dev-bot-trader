@echo off
chcp 65001 >nul
echo ========================================
echo ₿ INICIANDO ROBÔ - BITCOIN
echo ========================================
echo.
echo Moeda: BTCUSDT
echo Estratégia: Double EMA Breakout + IA
echo Modo: Simulação
echo.
echo Pressione CTRL+C para parar o robô
echo ========================================
echo.
set PYTHONIOENCODING=utf-8
set PYTHONPATH=backend/src
python backend/src/live_trading/double_ema_breakout_orders_long_short_dual_params_agent_evaluator.py --cripto BTCUSDT --is_simulator
pause
