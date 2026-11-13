# Script de inicio local para Amershop (Sin Docker) en PowerShell
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "   🛒 AMERSHOP - ASISTENTE IA CORPORATIVO (LOCAL)" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Comprobar Ollama
try {
    $res = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
    Write-Host "[OK] Motor Ollama detectado en http://localhost:11434" -ForegroundColor Green
} catch {
    Write-Host "[AVISO] Ollama no parece estar corriendo en http://localhost:11434" -ForegroundColor Yellow
    Write-Host "Descárgalo gratis de https://ollama.com y ejecuta: ollama run llama3.2" -ForegroundColor Yellow
}

# 2. Archivo .env
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "[OK] Archivo .env creado a partir de .env.example" -ForegroundColor Green
}

# 3. Iniciar Backend
Write-Host "Iniciando Backend FastAPI en puerto 8000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python -m uvicorn main:app --host 0.0.0.0 --port 8000"

Start-Sleep -Seconds 3

# 4. Iniciar Frontend
Write-Host "Iniciando Frontend Streamlit en puerto 8501..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; python -m streamlit run app.py --server.port 8501"

Write-Host ""
Write-Host "✅ Aplicación iniciada con éxito:" -ForegroundColor Green
Write-Host " - Landing Page & Chat: http://localhost:8501" -ForegroundColor White
Write-Host " - Backend API & Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Para detener la aplicación, cierra las ventanas de PowerShell abiertas." -ForegroundColor Gray
