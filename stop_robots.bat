@echo off
chcp 65001 >nul
echo ========================================
echo 🛑 PARANDO TODOS OS ROBÔS PYTHON
echo ========================================
echo.
echo Processos Python rodando:
echo.
tasklist | findstr python
echo.
echo ========================================
echo.
set /p confirm="Deseja parar TODOS os processos Python? (S/N): "
if /i "%confirm%"=="S" (
    echo.
    echo Parando processos...
    taskkill /F /IM python.exe
    echo.
    echo ✅ Todos os robôs foram parados!
) else (
    echo.
    echo ❌ Operação cancelada.
)
echo.
echo ========================================
pause
