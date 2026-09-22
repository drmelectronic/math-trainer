#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [[ -x ".venv/Scripts/python.exe" ]]; then
  VENV_PYTHON=".venv/Scripts/python.exe"
elif [[ -x ".venv/bin/python" ]]; then
  VENV_PYTHON=".venv/bin/python"
else
  echo "No se encontro el entorno virtual."
  echo "Ejecuta primero: ./install.sh"
  exit 1
fi

exec "${VENV_PYTHON}" -m math_trainer.main
