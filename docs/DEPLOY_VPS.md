# 🚀 Guía de Despliegue Paso a Paso en Servidor VPS
## Amershop — Agente IA Corporativo 100% Local (Sin Tokens)

Esta guía detalla el proceso completo para desplegar la plataforma **Amershop** en cualquier servidor virtual privado (**VPS**) ejecutando Linux (Ubuntu 22.04 LTS / 24.04 LTS o Debian 12), garantizando alta disponibilidad, seguridad, persistencia y funcionamiento **100% gratuito sin consumo de tokens ni APIs de pago**.

---

## 📋 1. Requisitos del Servidor VPS

| Perfil de Servidor | CPU | Memoria RAM | Disco SSD | Modelo Local Recomendado |
| :--- | :---: | :---: | :---: | :--- |
| **Económico / Básico** | 1 vCPU | 2 GB (+ 4GB Swap) | 25 GB | `llama3.2:1b` (Ultra liviano y rápido) |
| **Estándar (Recomendado)** | 2 vCPU | 4 GB (+ 4GB Swap) | 40 GB | `llama3.2` (3B parámetros, equilibrado) |
| **Avanzado / Concurrente** | 4 vCPU | 8–16 GB | 60 GB | `phi3:mini` o `mistral` |

> 💡 **Proveedores recomendados:** Hetzner Cloud (CX22 / CPX21), DigitalOcean (Droplet Basic), OVHcloud, Linode (Akamai), AWS Lightsail, o Oracle Cloud Free Tier (instancia ARM Ampere de hasta 24GB RAM gratuita).

---

## 🛠️ 2. Paso 1: Configuración Inicial de la VPS

Conéctate a tu VPS mediante SSH desde tu terminal (PowerShell, CMD o Terminal Linux/macOS):

```bash
ssh root@TU_IP_VPS
```

### 2.1 Actualizar el sistema operativo
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git ufw htop
```

### 2.2 Configurar memoria Swap (Esencial para servidores de 2GB a 4GB de RAM)
El archivo Swap evita que el proceso de Ollama o FAISS se cierre por falta de memoria física (*Out Of Memory*):

```bash
# Crear un archivo swap de 4 GB
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Hacerlo persistente tras reinicios
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

Verifica la activación con `free -h`.

---

## 🐳 3. Paso 2: Instalar Docker y Docker Compose v2

Instala la versión oficial más reciente de Docker con el script oficial automatizado:

```bash
# Descargar e instalar Docker Engine
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Habilitar inicio automático con el sistema
sudo systemctl enable docker
sudo systemctl start docker

# Verificar instalación
docker --version
docker compose version
```

---

## 📦 4. Paso 3: Clonar o Subir el Proyecto a la VPS

### Opción A: Clonar desde repositorio Git (Recomendada)
```bash
cd /opt
git clone https://github.com/Desarrollo-de-software-2-DAM/Agente.git amershop-agente
cd amershop-agente
```

### Opción B: Subir los archivos desde tu computadora local con SCP
Si tienes los archivos en tu PC con Windows:
```powershell
# Ejecuta en PowerShell de tu computadora local:
scp -r "c:\Users\amer\Desktop\Agente-1" root@TU_IP_VPS:/opt/amershop-agente
```
Luego en la VPS:
```bash
cd /opt/amershop-agente
```

---

## ⚙️ 5. Paso 4: Configurar Variables de Entorno (`.env`)

Crea tu archivo `.env` a partir de la plantilla:

```bash
cp .env.example .env
nano .env
```

Asegúrate de configurar valores seguros para tu entorno de producción:

```env
# --- Configuración General ---
STORE_NAME=Amershop

# --- Proveedor Local (Sin tokens ni costo) ---
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434
# Si tu VPS tiene 2GB de RAM usa llama3.2:1b; si tiene 4GB o más usa llama3.2
OLLAMA_MODEL=llama3.2
OLLAMA_TEMPERATURE=0.1

# --- Base de datos PostgreSQL (Cambia las contraseñas) ---
POSTGRES_USER=agente
POSTGRES_PASSWORD=PonUnaClaveMuySegura_12345
POSTGRES_DB=agente_db

# --- Contraseñas de usuarios corporativos iniciales ---
ADMIN_PASSWORD=AdminSeguro2026!
USER1_PASSWORD=ClaveCollab01!
USER2_PASSWORD=ClaveCollab02!
RRHH_PASSWORD=ClaveRRHH2026!
VENTAS_PASSWORD=ClaveVentas2026!
SOPORTE_PASSWORD=ClaveSoporte2026!
```

Guarda los cambios con `Ctrl + O`, presiona `Enter` y sal con `Ctrl + X`.

---

## 🚀 6. Paso 5: Despliegue con Docker Compose

Ejecuta la construcción e inicio en segundo plano:

```bash
docker compose up --build -d
```

### ¿Qué sucede durante este comando?
1. Se inicia **PostgreSQL 16** y crea la base de datos `agente_db`.
2. Se inicia el motor **Ollama Local**.
3. El servicio auxiliar `ollama-pull` contacta a Ollama y **descarga automáticamente el modelo `llama3.2`** (aprox. 2 GB).
4. El contenedor **Backend (FastAPI)** compila dependencias, siembra usuarios corporativos en PostgreSQL e **indexa los documentos de la tienda en FAISS**.
5. El contenedor **Frontend (Streamlit)** levanta la **Landing Page** y la interfaz de chat en el puerto `8501`.

### Monitorear el progreso del despliegue:
```bash
# Ver logs en tiempo real
docker compose logs -f

# O ver solo los logs del backend:
docker compose logs -f backend
```

Espera hasta observar:
```
Application startup complete.
✅ Modelo local descargado y listo para usar sin tokens.
```

---

## 🧪 7. Paso 6: Verificación y Testing en la VPS

### 7.1 Verificar contenedores activos
```bash
docker compose ps
```
Deberás ver los servicios con estado `Up` y `healthy`:
- `agente_db`: `Up (healthy)`
- `agente_ollama`: `Up (healthy)`
- `agente_backend`: `Up (healthy)`
- `agente_frontend`: `Up (healthy)`

### 7.2 Probar los endpoints REST vía cURL
```bash
# Health check general
curl http://localhost:8000/

# Estado detallado del sistema
curl http://localhost:8000/status
```

### 7.3 Ejecutar la suite completa de pruebas unitarias
Los tests con `pytest` ya están incluidos en la imagen del contenedor:

```bash
docker compose exec backend pytest tests -v
```

Deberás ver todas las pruebas aprobadas:
```
tests/test_api.py::test_health_check_endpoint PASSED
tests/test_api.py::test_register_success PASSED
tests/test_api.py::test_login_success PASSED
tests/test_api.py::test_chat_endpoint_with_mock_agent PASSED
tests/test_loaders.py::test_load_markdown PASSED
tests/test_loaders.py::test_normalizar_marca PASSED
tests/test_vectorstore.py::test_search_returns_relevant_document PASSED
tests/test_rag_agent.py::test_rag_agent_query_success PASSED
```

---

## 🔒 8. Paso 7: Configuración de Dominio, Nginx y SSL Gratuito (HTTPS)

Para poner tu aplicación en producción accesible bajo un dominio (ejemplo: `amershop.tudominio.com`):

### 8.1 Instalar Nginx y Certbot
```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

### 8.2 Crear configuración de Nginx con soporte WebSockets
Crea el archivo `/etc/nginx/sites-available/amershop.conf`:

```bash
sudo nano /etc/nginx/sites-available/amershop.conf
```

Pega la siguiente configuración (reemplaza `tu-dominio.com` por tu dominio real):

```nginx
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;

    # Frontend Streamlit (Landing + Chat)
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # Backend API Docs & Endpoints
    location /api/ {
        rewrite ^/api/(.*) /$1 break;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Habilita el sitio y reinicia Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/amershop.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 8.3 Obtener Certificado SSL Gratuito con Let's Encrypt
```bash
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com
```

Sigue las instrucciones en pantalla. Certbot renovará automáticamente los certificados antes de que expiren.

---

## 🛡️ 9. Paso 8: Configuración del Firewall (UFW)

Protege tu servidor cerrando puertos internos para que solo el tráfico web y SSH sea permitido:

```bash
# Permitir SSH (evita quedarte bloqueado)
sudo ufw allow 22/tcp

# Permitir tráfico web HTTP y HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Opcional: Si accedes directamente sin Nginx (solo en modo desarrollo):
# sudo ufw allow 8501/tcp
# sudo ufw allow 8000/tcp

# Activar el firewall
sudo ufw enable
sudo ufw status
```

---

## 🔄 10. Paso 9: Mantenimiento y Operaciones Frecuentes

### Reiniciar el sistema
```bash
cd /opt/amershop-agente
docker compose restart
```

### Detener los servicios sin perder datos
```bash
docker compose down
```

### Actualizar el código desde Git
```bash
git pull origin main
docker compose up --build -d
```

### Cambiar de modelo en Ollama (ej. cambiar a `llama3.2:1b`)
Edita tu `.env`:
```env
OLLAMA_MODEL=llama3.2:1b
```
Luego descarga el nuevo modelo y reinicia el backend:
```bash
docker exec -it agente_ollama ollama pull llama3.2:1b
docker compose restart backend
```

### Reindexar documentos tras modificar la carpeta `backend/documents/`
```bash
docker compose exec backend sh -c "rm -rf /app/chroma_db/*"
docker compose restart backend
```

### Realizar copia de seguridad de la base de datos PostgreSQL
```bash
docker exec -t agente_db pg_dump -U agente agente_db > backup_$(date +%Y%m%d).sql
```

---

## 🎯 Resumen de Accesos en Producción

- **Landing Page & Chat Web:** `https://tu-dominio.com` (o `http://TU_IP_VPS:8501`)
- **API REST Backend:** `https://tu-dominio.com/api/` (o `http://TU_IP_VPS:8000`)
- **Swagger UI (Documentación interactiva):** `http://TU_IP_VPS:8000/docs`
- **Consumo de tokens:** **0 TOKENS (100% Gratuito y Privado)**.
