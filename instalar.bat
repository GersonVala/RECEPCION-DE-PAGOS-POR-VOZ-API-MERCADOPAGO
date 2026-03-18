@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion
title HolaGranja - Instalador
color 0A

echo ============================================
echo    HolaGranja - Instalador Automatico
echo ============================================
echo.

:: -----------------------------------------------
:: PASO 1: Verificar si Python esta instalado
:: -----------------------------------------------
echo [1/6] Verificando Python...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  Python NO esta instalado en esta PC.
    echo  Descargando Python 3.12...
    echo.

    :: Descargar Python
    curl -L -o "%TEMP%\python_installer.exe" "https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"

    if not exist "%TEMP%\python_installer.exe" (
        echo  ERROR: No se pudo descargar Python.
        echo  Descargalo manualmente desde https://www.python.org/downloads/
        echo  IMPORTANTE: Marca "Add Python to PATH" durante la instalacion.
        pause
        exit /b 1
    )

    echo  Instalando Python silenciosamente...
    "%TEMP%\python_installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1

    if %ERRORLEVEL% NEQ 0 (
        echo  La instalacion silenciosa fallo. Abriendo instalador manual...
        echo  IMPORTANTE: Marca "Add Python to PATH" durante la instalacion.
        "%TEMP%\python_installer.exe"
    )

    del "%TEMP%\python_installer.exe" >nul 2>&1

    :: Refrescar PATH para esta sesion
    set "PATH=%LOCALAPPDATA%\Programs\Python\Python312\;%LOCALAPPDATA%\Programs\Python\Python312\Scripts\;%ProgramFiles%\Python312\;%ProgramFiles%\Python312\Scripts\;%PATH%"

    python --version >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo  ERROR: Python no se detecto tras la instalacion.
        echo  Puede que necesites REINICIAR la PC y ejecutar este instalador de nuevo.
        pause
        exit /b 1
    )
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo  OK - %PYVER% detectado
echo.

:: -----------------------------------------------
:: PASO 2: Instalar Cloudflared
:: -----------------------------------------------
echo [2/6] Verificando Cloudflared...
cloudflared --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  Cloudflared NO esta instalado. Descargando...
    echo.

    curl -L -o "%TEMP%\cloudflared.msi" "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.msi"

    if not exist "%TEMP%\cloudflared.msi" (
        echo  ERROR: No se pudo descargar Cloudflared.
        echo  Descargalo manualmente desde https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
        pause
        exit /b 1
    )

    echo  Instalando Cloudflared...
    msiexec /i "%TEMP%\cloudflared.msi" /quiet /norestart

    del "%TEMP%\cloudflared.msi" >nul 2>&1

    :: Refrescar PATH
    set "PATH=%ProgramFiles(x86)%\cloudflared\;%ProgramFiles%\cloudflared\;%PATH%"

    cloudflared --version >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo  ERROR: Cloudflared no se detecto tras la instalacion.
        echo  Puede que necesites REINICIAR la PC y ejecutar este instalador de nuevo.
        pause
        exit /b 1
    )
)

for /f "tokens=*" %%i in ('cloudflared --version 2^>^&1') do set CFVER=%%i
echo  OK - %CFVER% detectado
echo.

:: -----------------------------------------------
:: PASO 3: Instalar dependencias Python
:: -----------------------------------------------
echo [3/6] Instalando dependencias de Python...
cd /d "%~dp0"
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo  ERROR: Fallo al instalar dependencias.
    pause
    exit /b 1
)
echo  OK - Dependencias instaladas
echo.

:: -----------------------------------------------
:: PASO 4: Configurar .env con token de MercadoPago
:: -----------------------------------------------
echo [4/6] Configurando credenciales de MercadoPago...

if exist .env (
    echo  Ya existe un archivo .env, se conserva el existente.
    echo  Si necesitas cambiarlo, edita el archivo .env manualmente.
) else (
    echo.
    echo  Necesitas tu Access Token de MercadoPago.
    echo  Lo encontras en: https://www.mercadopago.com.ar/developers/panel/app
    echo.
    set /p "MP_TOKEN=  Ingresa tu MP_ACCESS_TOKEN: "
    echo.
    set /p "MP_PORT=  Puerto del servidor (presiona Enter para 5000): "

    if "!MP_PORT!"=="" set "MP_PORT=5000"

    (
        echo MP_ACCESS_TOKEN=!MP_TOKEN!
        echo FLASK_PORT=!MP_PORT!
    ) > .env

    echo  OK - Archivo .env creado
)
echo.

:: -----------------------------------------------
:: PASO 5: Configurar Cloudflare Tunnel
:: -----------------------------------------------
echo [5/6] Configurando Cloudflare Tunnel...
echo.
echo  Necesitas el token de tu tunnel de Cloudflare.
echo  Lo encontras en: Cloudflare Dashboard ^> Zero Trust ^> Networks ^> Tunnels
echo  Selecciona tu tunnel ^> Configure ^> copia el token del comando de instalacion.
echo.
echo  Ejemplo del comando que te muestra Cloudflare:
echo    cloudflared service install eyJhIGxvbmcgdG9rZW4...
echo                                 ^^^^^^^^^^^^^^^^^^^^^^^^
echo                                 Copia SOLO esta parte (el token)
echo.
set /p "CF_TOKEN=  Ingresa tu Cloudflare Tunnel Token: "

if "!CF_TOKEN!"=="" (
    echo  AVISO: No se ingreso token. El tunnel no se configurara.
    echo  Podes configurarlo despues con: cloudflared service install TU_TOKEN
) else (
    :: Instalar cloudflared como servicio de Windows con el token
    cloudflared service install !CF_TOKEN! 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo  OK - Cloudflare Tunnel instalado como servicio de Windows.
        echo  El tunnel se iniciara automaticamente con la PC.
    ) else (
        echo  AVISO: No se pudo instalar como servicio (puede que ya exista^).
        echo  Si ya estaba configurado, no hay problema.
    )
)
echo.

:: -----------------------------------------------
:: PASO 6: Crear tarea programada en Windows
:: -----------------------------------------------
echo [6/6] Registrando inicio automatico en Programador de Tareas...

set "SCRIPT_PATH=%~dp0iniciar_server.bat"

schtasks /query /tn "HolaGranja" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo  La tarea "HolaGranja" ya existe, actualizando...
    schtasks /delete /tn "HolaGranja" /f >nul 2>&1
)

schtasks /create /tn "HolaGranja" /tr "\"%SCRIPT_PATH%\"" /sc onlogon /rl highest /f >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo  OK - Tarea "HolaGranja" creada. El servidor se iniciara al encender la PC.
) else (
    echo  AVISO: No se pudo crear la tarea automaticamente.
    echo  Puede que necesites ejecutar este instalador como Administrador.
    echo  O puedes crear la tarea manualmente en el Programador de Tareas.
)
echo.

:: -----------------------------------------------
:: Resumen final
:: -----------------------------------------------
echo ============================================
echo  Instalacion completada! Resumen:
echo ============================================
echo.
echo  - Python: %PYVER%
echo  - Cloudflared: %CFVER%
echo  - Proyecto: %~dp0
echo  - Tunnel: holagranja.miguelkraus.uk
echo  - Inicio automatico: Si (servicio + tarea programada)
echo.
echo  Al encender la PC:
echo    1. Cloudflared inicia el tunnel (servicio de Windows)
echo    2. HolaGranja inicia el servidor Flask (Programador de Tareas)
echo    3. La web queda accesible en https://holagranja.miguelkraus.uk
echo.

set /p "INICIAR=Queres iniciar el servidor ahora? (S/N): "
if /i "!INICIAR!"=="S" (
    echo.
    echo Iniciando servidor...
    call "%~dp0iniciar_server.bat"
) else (
    echo.
    echo OK - Podes iniciarlo cuando quieras con iniciar_server.bat
)

pause
