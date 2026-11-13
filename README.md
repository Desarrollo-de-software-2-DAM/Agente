# 🛒 Amershop — Agente IA Corporativo 100% Local (Sin Tokens)

<p align="center">
  <img src="https://img.shields.io/badge/PYTHON-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.12">
  <img src="https://img.shields.io/badge/STREAMLIT-FRONTEND-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/FASTAPI-BACKEND-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/LANGCHAIN-RAG-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" alt="LangChain">
  <img src="https://img.shields.io/badge/LLM-OLLAMA%20LOCAL-000000?style=for-the-badge&logo=ollama&logoColor=white" alt="Ollama Local LLM">
  <img src="https://img.shields.io/badge/POSTGRESQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL 16">
  <img src="https://img.shields.io/badge/DOCKER-COMPOSE-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker Compose">
  <img src="https://img.shields.io/badge/TOKENS-0%20(GRATUITO)-brightgreen?style=for-the-badge" alt="0 Tokens">
</p>

<p align="center">
  <b>Plataforma inteligente corporativa con Landing Page integrada, Agente RAG local y despliegue automatizado para la tienda tecnológica Amershop.</b>
</p>

---

Responde consultas sobre envíos, devoluciones, garantías, métodos de pago, políticas y catálogo de productos basándose estrictamente en los documentos internos de la empresa (**RAG**: *Retrieval-Augmented Generation*), ejecutándose **100% en local mediante Ollama, sin necesidad de tokens ni costos de API externos**.

> 🚀 Proyecto de **Desarrollo de Software II**: arquitectura de microservicios con Docker Compose, Landing Page interactiva, autenticación segura con PostgreSQL, base de datos vectorial FAISS y guía de despliegue en VPS Linux.

---

## ⚡ Inicio Rápido (En 1 Solo Comando)

No requiere API keys ni tokens de pago. Solo necesitas Docker Desktop (o Docker con Compose v2 en Linux) y Git.

```bash
# 1. Clonar el repositorio
git clone https://github.com/Desarrollo-de-software-2-DAM/Agente.git
cd Agente

# 2. Crear archivo de variables de entorno
cp .env.example .env        # Windows CMD: copy .env.example .env

# 3. Construir y levantar todos los servicios con Docker Compose
docker compose up --build
```

Cuando los contenedores indiquen estado **healthy**, abre tu navegador en:
- 🌐 **Landing Page & Chat Web:** <http://localhost:8501>
- ⚡ **API REST del Backend:** <http://localhost:8000>
- 📖 **Documentación Swagger UI:** <http://localhost:8000/docs>

---

## 📑 Contenido

1. [Descripción general](#-1-descripción-general)
2. [Landing Page y Conectividad](#-2-landing-page-y-conectividad)
3. [Arquitectura del Sistema](#-3-arquitectura-del-sistema)
4. [Estructura del Proyecto](#-4-estructura-del-proyecto)
5. [Tecnologías Utilizadas](#-5-tecnologías-utilizadas)
6. [Configuración: Variables de Entorno](#-6-configuración-variables-de-entorno)
7. [Ejecución con Docker Compose](#-7-ejecución-con-docker-compose)
8. [Despliegue Paso a Paso en VPS](#-8-despliegue-paso-a-paso-en-vps)
9. [Suite de Testing Automatizado](#-9-suite-de-testing-automatizado)
10. [API REST del Backend](#-10-api-rest-del-backend)
11. [Fuentes de Datos y Base de Conocimiento](#-11-fuentes-de-datos-y-base-de-conocimiento)
12. [Solución de Problemas (Troubleshooting)](#-12-solución-de-problemas-troubleshooting)
13. [Equipo y Licencia](#-13-equipo-y-licencia)

---

## 📋 1. Descripción General

El sistema opera con **cuatro contenedores principales** orquestados mediante Docker Compose:

| Componente | Tecnología | Función |
| :--- | :--- | :--- |
| **Frontend** | Streamlit | **Landing Page corporativa**, autenticación, historial y chat interactivo con el asistente. |
| **Backend** | FastAPI + RAG | API REST, orquestación RAG, autenticación bcrypt, normalización y búsqueda híbrida. |
| **Motor LLM Local** | Ollama | Ejecución local del modelo Llama 3.2 (sin tokens, sin APIs de pago, 100% privado). |
| **Base de Datos** | PostgreSQL 16 | Almacenamiento relacional de usuarios, credenciales y persistencia de chats. |

### Principales Ventajas
- 🪙 **0 Tokens consumidos:** El modelo corre dentro del contenedor Ollama en tu propio servidor/computadora.
- 🎯 **Respuestas sin alucinaciones:** Responde únicamente con el contexto extraído de los documentos oficiales; si la respuesta no está en la base de conocimiento, lo indica claramente.
- 🔍 **Búsqueda híbrida:** Fusión de búsqueda vectorial densa (**FAISS** con MMR) y búsqueda léxica normalizada con sinónimos en español (*Reciprocal Rank Fusion*).
- 📂 **Multi-formato de ingesta (8 formatos):** PDF, DOCX, XLSX, PPTX, Markdown, CSV, JSON y HTML.
- 🔐 **Seguridad empresarial:** Contraseñas protegidas mediante hash `bcrypt`, usuarios corporativos precargados (`admin`, `ventas`, `soporte`, etc.) y registro abierto.

---

## 🌐 2. Landing Page y Conectividad

La interfaz web (<http://localhost:8501>) cuenta con una **Landing Page de bienvenida** que conecta todos los módulos de la aplicación:

1. **Sección Hero:** Resumen visual del agente IA local, badges de estado y botones de llamado a la acción (CTA) para entrar al chat, iniciar sesión o acceder como invitado.
2. **Indicadores en Tiempo Real:** Monitorización en vivo del estado del backend, motor LLM activo, número de fragmentos indexados en FAISS y consumo de tokens.
3. **Malla de Características:** Tarjetas interactivas con las ventajas clave (Búsqueda híbrida, 8 formatos, PostgreSQL, Docker).
4. **Diagrama de Arquitectura Integrada:** Visualización del flujo de peticiones entre Frontend, Backend, Ollama, PostgreSQL y FAISS.
5. **Referencia de la API REST:** Tabla con los endpoints disponibles y comandos cURL de ejemplo.
6. **Navegación Fluida:** Barra lateral que permite alternar entre la Landing Page, el Chat IA y la pantalla de Autenticación sin perder el contexto.

---

## 🏗️ 3. Arquitectura del Sistema

```
                         Navegador Web / Clientes Externos
                                      │
                                      │  http://localhost:8501
                                      ▼
                      ┌──────────────────────────────┐
                      │    frontend  (Streamlit)     │
                      │   Landing Page + Chat + Auth │
                      └──────────────┬───────────────┘
                                     │  HTTP (Puerto 8000)
                                     ▼
                      ┌──────────────────────────────┐
                      │    backend  (FastAPI + RAG)  │
                      │  Endpoints REST + Normalizer │
                      └──────┬───────────────┬───────┘
                             │               │
                 SQL (psycopg)               │ Búsqueda Híbrida
                             │               ▼
            ┌────────────────┴───┐     ┌────────────────────────────┐
            │ db (PostgreSQL 16) │     │ FAISS + FastEmbed          │
            │ Usuarios + Historial│     │ Índice vectorial en disco  │
            └────────────────────┘     └────────────────────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │   ollama  (Agente Local)     │
              │  Llama 3.2 · Cero Tokens     │
              └──────────────────────────────┘
```

---

## 📁 4. Estructura del Proyecto

```
Agente/
├── docker-compose.yml          # Orquestación de db, ollama, backend y frontend
├── .env.example                # Plantilla de variables de entorno (Ollama, BD)
├── .env                        # Variables locales (ignorado en Git)
├── README.md                   # Documentación principal
├── docs/
│   ├── DEPLOY_VPS.md           # Guía paso a paso para desplegar en VPS Linux
│   ├── CONTRADICCIONES.md      # Fuentes únicas de verdad y resolución de conflictos
│   ├── CONTRIBUTION.md         # Flujo de trabajo Git, ramas y pull requests
│   └── evidencias/             # Capturas de ejecución y pruebas
├── backend/
│   ├── Dockerfile              # Imagen Python 3.12 con curl y pytest incluidos
│   ├── main.py                 # FastAPI: endpoints /chat, /login, /register, /status
│   ├── config.py               # Configuración centralizada (Ollama / Gemini / RAG)
│   ├── db.py                   # Modelos SQLAlchemy, sesiones y hash bcrypt
│   ├── requirements.txt        # Dependencias de producción
│   ├── requirements-dev.txt    # Dependencias de testing (pytest, httpx)
│   ├── agents/
│   │   ├── rag_agent.py        # Agente RAG con soporte local para Ollama
│   │   └── document_grader.py  # Evaluador de relevancia local
│   ├── loaders/
│   │   └── multi_loader.py     # Carga de 8 formatos (PDF, DOCX, XLSX, etc.)
│   ├── vectorstore/
│   │   └── faiss_store.py     # Índice vectorial FAISS y búsqueda híbrida
│   ├── utils/
│   │   └── text_normalize.py   # Expansión de sinónimos y búsqueda léxica
│   ├── scripts/
│   │   ├── generar_datos_oficiales.py  # Generador de datos_oficiales.md
│   │   └── auditar_datos.py            # Auditor de inconsistencias regionales
│   ├── documents/              # Documentos y base de conocimiento de la tienda
│   └── tests/                  # Suite completa de pruebas automatizadas
│       ├── conftest.py         # Base de datos SQLite en memoria y fixtures
│       ├── test_api.py         # Tests de endpoints REST
│       ├── test_loaders.py     # Tests de ingesta multi-formato
│       ├── test_vectorstore.py # Tests de FAISS y búsqueda híbrida
│       ├── test_rag_agent.py   # Tests del ciclo RAG con LLM simulado
│       ├── test_busqueda_normalizacion.py
│       └── test_datos_consistentes.py
└── frontend/
    ├── Dockerfile              # Imagen optimizada para Streamlit
    ├── app.py                  # Router de vistas, sidebar y chat
    ├── landing.py              # Landing Page corporativa con indicadores en vivo
    ├── requirements.txt
    ├── .streamlit/config.toml  # Tema visual oscuro personalizado
    └── assets/                 # Logo e imágenes corporativas
```

---

## 🛠️ 5. Tecnologías Utilizadas

- **Backend:** Python 3.12, FastAPI, Uvicorn, SQLAlchemy, Pydantic, Bcrypt, Psycopg.
- **Frontend:** Streamlit con diseño UI moderno (*Outfit font*, tema violeta/oscuro).
- **Inteligencia Artificial Local:** Ollama con `llama3.2` (sin tokens), LangChain Ollama.
- **Base de Datos Vectorial:** FAISS (`faiss-cpu`), FastEmbed (`BAAI/bge-small-en-v1.5`), Reciprocal Rank Fusion.
- **Base de Datos Relacional:** PostgreSQL 16 Alpine.
- **Contenedores:** Docker y Docker Compose v2.
- **Testing:** Pytest, HTTPX, TestClient de FastAPI, Fixtures en memoria.

---

## ⚙️ 6. Configuración: Variables de Entorno

El archivo `.env` en la raíz controla toda la configuración. Puedes partir de `.env.example`:

```env
# --- General ---
STORE_NAME=Amershop

# --- Agente Local (Sin Tokens) ---
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2
OLLAMA_TEMPERATURE=0.1

# --- Base de Datos PostgreSQL ---
POSTGRES_USER=agente
POSTGRES_PASSWORD=cambia_esta_clave_segura
POSTGRES_DB=agente_db

# --- Contraseñas de Usuarios Corporativos ---
ADMIN_PASSWORD=amershop2024
USER1_PASSWORD=collab001
USER2_PASSWORD=collab002
RRHH_PASSWORD=recursosh01
VENTAS_PASSWORD=ventas2024
SOPORTE_PASSWORD=soporte01
```

---

## 🐳 7. Ejecución con Docker Compose

Para levantar toda la solución en tu máquina local:

```bash
docker compose up --build -d
```

### Comandos útiles para la gestión de contenedores:
```bash
# Ver estado de salud de los servicios
docker compose ps

# Monitorear logs del backend
docker compose logs -f backend

# Monitorear logs de Ollama
docker compose logs -f ollama

# Detener los servicios conservando base de datos e índices
docker compose down

# Detener y borrar volúmenes de datos
docker compose down -v
```

---

## 🚀 8. Despliegue Paso a Paso en VPS

Para desplegar la aplicación en un servidor en la nube (Ubuntu / Debian en Hetzner, DigitalOcean, AWS, Oracle Cloud, etc.), consulta la guía detallada:

👉 **[Guía Completa de Despliegue en VPS (docs/DEPLOY_VPS.md)](docs/DEPLOY_VPS.md)**

Incluye:
- Requisitos mínimos de hardware (CPU, RAM, disco).
- Configuración de memoria Swap para evitar *Out-of-Memory*.
- Instalación de Docker y Docker Compose v2.
- Configuración de Nginx Reverse Proxy con soporte WebSockets.
- Certificado SSL gratuito con Let's Encrypt (HTTPS).
- Reglas de cortafuegos UFW para proteger puertos internos.

---

## 🧪 9. Suite de Testing Automatizado

La suite de pruebas con `pytest` valida de forma aislada los endpoints de la API, la ingesta de documentos, la persistencia en base de datos y la búsqueda híbrida.

### Ejecución dentro del contenedor de Docker (Recomendada):
```bash
docker compose exec backend pytest tests -v
```

### Ejecución local en tu equipo (con entorno virtual):
```bash
cd backend
pip install -r requirements.txt -r requirements-dev.txt
pytest tests -v
```

---

## 🔌 10. API REST del Backend

| Método | Endpoint | Descripción |
| :---: | :--- | :--- |
| `GET` | `/` | Comprobación de estado general (*healthcheck*). |
| `GET` | `/status` | Métricas en tiempo real: estado de BD, proveedor LLM y documentos indexados. |
| `POST` | `/chat` | Envía una consulta al agente RAG (`prompt`, `chat_history`, `username` opcional). |
| `POST` | `/login` | Valida credenciales de usuario (`username`, `password`). |
| `POST` | `/register` | Registra una nueva cuenta de usuario con hash `bcrypt`. |
| `GET` | `/history/{username}` | Retorna el historial de chat persistido en PostgreSQL. |
| `GET` | `/docs` | Interfaz interactiva Swagger UI / OpenAPI. |

---

## 🩺 12. Solución de Problemas (Troubleshooting)

| Síntoma | Causa Probable | Solución |
| :--- | :--- | :--- |
| El frontend dice "No se pudo conectar con el servicio Backend" | El backend aún se encuentra indexando documentos o compilando. | Revisa con `docker compose logs -f backend` hasta ver `Application startup complete`. |
| El agente dice "No se pudo conectar con Ollama" | El contenedor `agente_ollama` está iniciando o el modelo se está descargando. | Espera 1 minuto a que `ollama-pull` termine la descarga o ejecuta: `docker exec -it agente_ollama ollama pull llama3.2`. |
| Servidor VPS con poca RAM se cuelga | La VPS no tiene memoria Swap habilitada y se satura la RAM física. | Sigue la [sección 2.2 de la guía de VPS](docs/DEPLOY_VPS.md) para habilitar 4GB de Swap o cambia a `OLLAMA_MODEL=llama3.2:1b`. |
| `password authentication failed for user "agente"` | Se cambió la contraseña en `.env` pero el volumen `pgdata` mantiene la anterior. | Ejecuta `docker compose down -v` y vuelve a levantar con `docker compose up -d`. |
| Se actualizaron documentos en `backend/documents/` pero el agente no los refleja | El índice FAISS ya estaba creado en el volumen `faiss_data`. | Ejecuta: `docker compose exec backend sh -c "rm -rf /app/chroma_db/*"` y reinicia con `docker compose restart backend`. |

---

## 🛡️ 13. Equipo y Licencia

Desarrollado para el curso **Desarrollo de Software II**:
- [@Amerx12](https://github.com/Amerx12)
- [@andres150921](https://github.com/andres150921)
- [@DanielJH414](https://github.com/DanielJH414)

Proyecto académico para **Amershop** — Plataforma Corporativa de IA. Todos los derechos reservados.
