@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo No se encontro el entorno virtual.
  echo Ejecuta primero: install.bat
  exit /b 1
)

set "PYTHONPATH=%CD%\src"
".venv\Scripts\python.exe" -m math_trainer.main
