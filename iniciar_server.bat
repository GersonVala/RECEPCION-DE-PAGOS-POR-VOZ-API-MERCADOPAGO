@echo off
:: ============================================
:: HolaGranja - Iniciar servidor
:: ============================================
cd /d "%~dp0"

echo Iniciando servidor HolaGranja...
echo (Cloudflare Tunnel corre como servicio de Windows)
echo.
python app.py
pause
