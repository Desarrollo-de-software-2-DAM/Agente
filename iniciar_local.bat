@echo off
chcp 65001 > nul
title Amershop - Inicio Local (Sin Docker)

echo =======================================================
echo    🛒 AMERSHOP - ASISTENTE IA CORPORATIVO (LOCAL)
echo =======================================================
echo.
echo Iniciando servicios en tu maquina local sin Docker...
echo.

:: 1. Verificar si Ollama esta corriendo
curl -s http://localhost:11434/api/tags > nul 2>&1
if %errorlevel% neq 0 (
    echo [AVISO] Ollama no parece estar ejecutandose en http://localhost:11434
    echo Si deseas respuestas de IA, abre Ollama o descargalo gratis desde:
    echo https://ollama.com
    echo Luego ejecuta en otra terminal: ollama run llama3.2
    echo.
) else (
    echo [OK] Motor Ollama detectado en http://localhost:11434
)

:: 2. Crear archivo .env si no existe
if not exist .env (
    echo Creando archivo .env a partir de .env.example...
    copy .env.example .env > nul
)

:: 3. Iniciar Backend FastAPI en una ventana nueva
echo Iniciando Backend (FastAPI) en el puerto 8000...
start "Amershop - Backend FastAPI" cmd /k "cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000"

:: 4. Esperar 3 segundos para que el backend inicie
timeout /t 3 /nobreak > nul

:: 5. Iniciar Frontend Streamlit en una ventana nueva
echo Iniciando Frontend (Streamlit) en el puerto 8501...
start "Amershop - Frontend Streamlit" cmd /k "cd frontend && python -m streamlit run app.py --server.port 8501"

echo.
echo =======================================================
echo    ✅ APLICACION INICIADA CON EXITO
echo =======================================================
echo - Landing Page y Chat: http://localhost:8501
echo - Backend API y Docs:  http://localhost:8000/docs
echo.
echo Para detener los servicios, simplemente cierra las ventanas de terminal abiertas.
echo.
pause
