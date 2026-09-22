@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ==^> Math Trainer - instalacion

set "PY="
where py >nul 2>&1 && (
  py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
  if not errorlevel 1 set "PY=py -3"
)
if not defined PY (
  where python >nul 2>&1 && (
    python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
    if not errorlevel 1 set "PY=python"
  )
)
if not defined PY (
  echo Error: se requiere Python 3.11 o superior ^(64 bits recomendado^).
  echo Descarga Python desde https://www.python.org/downloads/
  echo y marca "Add python.exe to PATH".
  exit /b 1
)

echo Usando: %PY%

if not exist ".venv\Scripts\python.exe" (
  echo ==^> Creando entorno virtual en .venv
  %PY% -m venv .venv
  if errorlevel 1 exit /b 1
)

set "VENV_PYTHON=.venv\Scripts\python.exe"

echo ==^> Instalando dependencias
"%VENV_PYTHON%" -m pip --version >nul 2>&1
if errorlevel 1 "%VENV_PYTHON%" -m ensurepip --upgrade

"%VENV_PYTHON%" -m pip install --upgrade pip
if errorlevel 1 exit /b 1

echo ==^> Instalando pygame ^(wheel precompilado^)
"%VENV_PYTHON%" -m pip install --only-binary=:all: "pygame>=2.6.0"
if errorlevel 1 (
  echo Error: no hay wheel de pygame para esta version de Python.
  echo Prueba con Python 3.11, 3.12 o 3.13 de 64 bits.
  exit /b 1
)

echo ==^> Instalando math-trainer
"%VENV_PYTHON%" -m pip install -e . --no-deps
if errorlevel 1 exit /b 1

echo.
echo Instalacion completa.
echo Ejecuta el juego con: run.bat
exit /b 0
