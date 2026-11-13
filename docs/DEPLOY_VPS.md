# Guía de despliegue de Amershop en una VPS

Esta guía describe una instalación de Amershop en un servidor Linux con Docker Compose. El despliegue usa PostgreSQL, Ollama, FastAPI y Streamlit. Ajustar los recursos del servidor al modelo de Ollama y al volumen de documentos; no existe un consumo de memoria único para todos los modelos.

> Esta guía es de despliegue técnico. Antes de exponer el sistema a Internet, revisar las notas de seguridad de este documento y reforzar la autenticación/autorización del backend.

## 1. Requisitos

- VPS con Ubuntu 22.04/24.04 o Debian 12, o una distribución Linux compatible con Docker Engine.
- Acceso SSH con permisos para instalar paquetes y administrar el firewall.
- Git, Docker Engine y Docker Compose v2.
- Memoria, CPU y disco suficientes para PostgreSQL, el modelo de Ollama, embeddings e índice. Revisar el consumo real con `free -h`, `df -h` y `docker stats`.
- Dominio apuntando a la IP pública si se configurará HTTPS con Nginx y Certbot.

## 2. Preparar el servidor

Conectarse por SSH:

```bash
ssh usuario@IP_DE_LA_VPS
```

Actualizar e instalar utilidades:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git ufw htop
```

La memoria Swap puede ayudar a evitar cierres por presión de memoria, pero no sustituye la RAM ni garantiza que cualquier modelo pueda ejecutarse con buen rendimiento. Si se habilita Swap, dimensionarla según el disco disponible y las necesidades del servidor.

## 3. Instalar Docker

Instalar Docker Engine y el plugin Compose siguiendo la documentación oficial de Docker para la distribución del servidor. Después comprobar:

```bash
docker --version
docker compose version
sudo systemctl enable --now docker
```

Si el usuario de despliegue no pertenece al grupo `docker`, ejecutar los comandos con `sudo`.

## 4. Obtener el proyecto

Clonar el repositorio:

```bash
sudo mkdir -p /opt
sudo chown "$USER":"$USER" /opt
cd /opt
git clone https://github.com/Desarrollo-de-software-2-DAM/Agente.git amershop-agente
cd /opt/amershop-agente
git switch develop
git pull origin develop
```

Si el equipo entrega una rama aprobada distinta, utilizar esa referencia en lugar de `develop`.

## 5. Configurar variables de entorno

Crear el archivo local:

```bash
cp .env.example .env
nano .env
```

Configuración base para Ollama en Compose:

```env
STORE_NAME=Amershop
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2
OLLAMA_TEMPERATURE=0.1

POSTGRES_USER=agente
POSTGRES_PASSWORD=REEMPLAZAR_POR_UNA_CLAVE_LARGA_Y_UNICA
POSTGRES_DB=agente_db

ADMIN_PASSWORD=REEMPLAZAR
USER1_PASSWORD=REEMPLAZAR
USER2_PASSWORD=REEMPLAZAR
RRHH_PASSWORD=REEMPLAZAR
VENTAS_PASSWORD=REEMPLAZAR
SOPORTE_PASSWORD=REEMPLAZAR

HF_TOKEN=
GOOGLE_API_KEY=
```

`GOOGLE_API_KEY` no se requiere cuando `LLM_PROVIDER=ollama`. No utilizar las contraseñas de ejemplo en un servidor real. Proteger el archivo:

```bash
chmod 600 .env
```

## 6. Construir e iniciar

Desde `/opt/amershop-agente`:

```bash
docker compose up -d --build
```

Revisar el estado:

```bash
docker compose ps
```

Revisar los logs si algún servicio no queda saludable:

```bash
docker compose logs --tail=150 db
docker compose logs --tail=150 ollama
docker compose logs --tail=150 ollama-pull
docker compose logs --tail=150 backend
docker compose logs --tail=150 frontend
```

`ollama-pull` es un servicio auxiliar que descarga el modelo y finaliza. Su estado `Exited` puede ser correcto cuando terminó con código cero. El backend depende de la finalización correcta de ese servicio y de la disponibilidad de PostgreSQL.

Comprobar los endpoints desde la propia VPS:

```bash
curl http://localhost:8000/
curl http://localhost:8000/status
```

La interfaz queda en `http://IP_DE_LA_VPS:8501` mientras se mantenga la publicación de puerto actual. Para un despliegue detrás de Nginx, seguir la sección 7.

## 7. Nginx y HTTPS

### 7.1 Importante: limitar la exposición de los puertos

El `docker-compose.yml` de desarrollo publica actualmente los puertos `8000:8000` y `8501:8501` en todas las interfaces del host. Para una VPS detrás de Nginx, cambiar esas publicaciones a loopback:

```yaml
backend:
  ports:
    - "127.0.0.1:8000:8000"

frontend:
  ports:
    - "127.0.0.1:8501:8501"
```

No publicar PostgreSQL. Ollama ya está enlazado a `127.0.0.1:11434` en el Compose revisado. Después de modificar Compose:

```bash
docker compose up -d
```

### 7.2 Instalar Nginx y Certbot

```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

Crear `/etc/nginx/sites-available/amershop` y ajustar el dominio:

```nginx
server {
    listen 80;
    server_name amershop.ejemplo.com;

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

Habilitar y validar:

```bash
sudo ln -s /etc/nginx/sites-available/amershop /etc/nginx/sites-enabled/amershop
sudo nginx -t
sudo systemctl reload nginx
```

Emitir el certificado cuando el DNS ya apunte a la VPS y los puertos 80/443 estén accesibles:

```bash
sudo certbot --nginx -d amershop.ejemplo.com
```

Después de habilitar HTTPS, comprobar la renovación automática con `sudo certbot renew --dry-run`.

## 8. Firewall

Permitir SSH antes de habilitar el firewall para evitar perder el acceso remoto:

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

No abrir públicamente los puertos 5432 ni 11434. Si Nginx se utiliza como entrada, tampoco abrir 8000 ni 8501 a Internet; mantenerlos en loopback como se indicó en la sección 7.

## 9. Actualización y mantenimiento

Actualizar código desde la rama de integración:

```bash
cd /opt/amershop-agente
git switch develop
git pull origin develop
docker compose up -d --build
```

Revisar estado y logs:

```bash
docker compose ps
docker compose logs --tail=100 backend frontend
```

Detener sin eliminar volúmenes:

```bash
docker compose down
```

Iniciar nuevamente:

```bash
docker compose up -d
```

### Copia de seguridad de PostgreSQL

```bash
docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > backup_amershop_$(date +%Y%m%d).sql
```

Guardar el respaldo fuera de la VPS y verificar periódicamente que pueda restaurarse.

### Nota sobre el índice FAISS

En la versión del código revisada, `VectorStoreManager` usa por defecto `./chroma_db/`, mientras que Compose monta `faiss_data` en `/app/faiss_db`. Esa discrepancia debe corregirse en código o en el punto de montaje antes de considerar persistente el índice en un volumen Docker. No borrar manualmente ninguna ruta de índice sin confirmar dónde está almacenado el índice utilizado por la instancia.

## 10. Consideraciones de seguridad antes de uso público

- Cambiar todas las contraseñas de `.env` y mantenerlo fuera de Git.
- Exponer solo Nginx (80/443); mantener API, Ollama y PostgreSQL restringidos.
- Revisar y restringir CORS: el backend actual permite todos los orígenes (`allow_origins=["*"]`).
- Revisar autenticación y autorización: la API actual verifica credenciales en login, pero no utiliza JWT/sesiones para proteger los endpoints de historial y chat. No tratar esta versión como una plataforma lista para producción con datos sensibles.
- Configurar copias de seguridad y probar restauraciones.
- Mantener imágenes, dependencias y sistema operativo actualizados.
