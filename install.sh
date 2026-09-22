#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo "==> Math Trainer - instalacion"

find_python() {
  local candidates=()
  if command -v py >/dev/null 2>&1; then
    candidates+=("py -3.13" "py -3")
  fi
  candidates+=("python3.13" "python3" "python")

  local candidate
  for candidate in "${candidates[@]}"; do
    if ! command -v ${candidate%% *} >/dev/null 2>&1; then
      continue
    fi

    if ${candidate} -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 13) else 1)' >/dev/null 2>&1; then
      echo "${candidate}"
      return 0
    fi
  done

  return 1
}

if ! PYTHON=$(find_python); then
  echo "Error: se requiere Python 3.13 o superior."
  echo "Windows: instala Python desde https://www.python.org/downloads/"
  echo "         y marca la opcion 'Add python.exe to PATH'."
  exit 1
fi

echo "Usando: ${PYTHON}"

if [[ -x ".venv/Scripts/python.exe" ]]; then
  VENV_PYTHON=".venv/Scripts/python.exe"
elif [[ -x ".venv/bin/python" ]]; then
  VENV_PYTHON=".venv/bin/python"
else
  echo "==> Creando entorno virtual en .venv"
  ${PYTHON} -m venv .venv
  if [[ -x ".venv/Scripts/python.exe" ]]; then
    VENV_PYTHON=".venv/Scripts/python.exe"
  else
    VENV_PYTHON=".venv/bin/python"
  fi
fi

echo "==> Instalando dependencias"
if ! "${VENV_PYTHON}" -m pip --version >/dev/null 2>&1; then
  "${VENV_PYTHON}" -m ensurepip --upgrade
fi
"${VENV_PYTHON}" -m pip install --upgrade pip
"${VENV_PYTHON}" -m pip install -e .

echo
echo "Instalacion completa."
echo "Ejecuta el juego con: ./run.sh"
