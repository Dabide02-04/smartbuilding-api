#!/usr/bin/env bash
set -e

cd /home/debian/smartbuilding-api

source "$HOME/.nvm/nvm.sh"
nvm use --silent default
source .venv/bin/activate

echo "Iniciando PostgreSQL..."
docker compose up -d --wait --wait-timeout 60

PID_API=""
PID_WEB=""

cerrar() {
    if [ -n "$PID_API" ]; then
        kill "$PID_API" 2>/dev/null || true
    fi
    if [ -n "$PID_WEB" ]; then
        kill "$PID_WEB" 2>/dev/null || true
    fi
}

trap cerrar EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

esperar() {
    for intento in {1..60}; do
        if ! kill -0 "$2" 2>/dev/null; then
            return 1
        fi
        if curl -fsS "$1" >/dev/null 2>&1; then
            return 0
        fi
        sleep 1
    done
    return 1
}

echo "Iniciando API..."
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 &
PID_API=$!

echo "Iniciando pagina..."
node frontend/node_modules/vite/bin/vite.js frontend --host 127.0.0.1 --port 5173 --strictPort &
PID_WEB=$!

esperar http://127.0.0.1:8000/ "$PID_API" || {
    echo "La API no pudo iniciar. Revisa el error de arriba."
    exit 1
}

esperar http://127.0.0.1:5173/ "$PID_WEB" || {
    echo "La pagina no pudo iniciar. Revisa el error de arriba."
    exit 1
}

xdg-open http://localhost:5173 >/dev/null 2>&1 &

echo "SmartBuilding iniciado."
echo "Deja esta terminal abierta. Para detenerlo, pulsa Ctrl+C."

wait -n "$PID_API" "$PID_WEB"
