#!/usr/bin/env bash
# Script de inicio local para Amershop (Sin Docker) en Linux / macOS

echo "======================================================="
echo "   🛒 AMERSHOP - ASISTENTE IA CORPORATIVO (LOCAL)"
echo "======================================================="
echo ""

# 1. Comprobar Ollama
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "[OK] Motor Ollama detectado en http://localhost:11434"
else
    echo "[AVISO] Ollama no está corriendo en http://localhost:11434"
    echo "Instálalo o ejecútalo con: ollama run llama3.2"
fi

# 2. Archivo .env
if [ ! -f .env ]; then
    cp .env.example .env
    echo "[OK] Archivo .env generado."
fi

# 3. Iniciar Backend en segundo plano
echo "Iniciando Backend FastAPI en http://localhost:8000..."
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

sleep 3

# 4. Iniciar Frontend
echo "Iniciando Frontend Streamlit en http://localhost:8501..."
cd frontend
python -m streamlit run app.py --server.port 8501 &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Aplicación iniciada con éxito:"
echo " - Landing Page & Chat: http://localhost:8501"
echo " - Backend API & Docs:  http://localhost:8000/docs"
echo ""
echo "Presiona Ctrl+C para detener ambos servicios."

trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT TERM
wait
