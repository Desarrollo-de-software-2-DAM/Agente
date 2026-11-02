# 🛒 Amershop — Agente IA Corporativo

<p align="center">
  <img src="https://img.shields.io/badge/PYTHON-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.12">
  <img src="https://img.shields.io/badge/STREAMLIT-FRONTEND-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/FASTAPI-BACKEND-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/LANGCHAIN-RAG-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" alt="LangChain">
  <img src="https://img.shields.io/badge/AGENT-GEMINI-4285F4?style=for-the-badge&logo=googlegemini&logoColor=white" alt="Google Gemini">
  <img src="https://img.shields.io/badge/POSTGRESQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL 16">
  <img src="https://img.shields.io/badge/DOCKER-COMPOSE-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker Compose">
</p>

<p align="center">
  <b>Asistente virtual inteligente de atención y consulta corporativa para la tienda de tecnología Amershop.</b>
</p>

---

Responde preguntas sobre envíos, devoluciones, garantías, métodos de pago, políticas y catálogo de productos, basándose únicamente en los documentos internos de la empresa (arquitectura **RAG**: *Retrieval-Augmented Generation*).

> Proyecto académico de **Desarrollo de Software II**: gestión de un proyecto mediante prácticas DevOps (control de versiones, contenedores con Docker y Docker Compose y, en la siguiente entrega, CI/CD con Jenkins).

## ⚡ Inicio rápido

Requiere Docker (con Compose v2), Git y una API Key de Google Gemini.

```bash
git clone https://github.com/Desarrollo-de-software-2-DAM/Agente.git
cd Agente
git checkout develop
cp .env.example .env        # Windows (CMD): copy .env.example .env
# Edita .env y escribe tu GOOGLE_API_KEY
docker compose up --build
```

Cuando el backend aparezca como *healthy*, abre <http://localhost:8501>. Los detalles están en la [sección 7](#-7-ejecución-con-docker-compose-recomendada).

---

## 📑 Contenido

1. [Descripción general](#-1-descripción-general)
2. [Arquitectura](#-2-arquitectura)
3. [Estructura del repositorio](#-3-estructura-del-repositorio)
4. [Tecnologías](#-4-tecnologías)
5. [Requisitos previos](#-5-requisitos-previos)
6. [Configuración: variables de entorno](#-6-configuración-variables-de-entorno)
7. [Ejecución con Docker Compose (recomendada)](#-7-ejecución-con-docker-compose-recomendada)
8. [Instalación tradicional (sin Docker)](#-8-instalación-tradicional-sin-docker)
9. [Uso de la aplicación](#-9-uso-de-la-aplicación)
10. [API del backend](#-10-api-del-backend)
11. [Pruebas y datos de la tienda](#-11-pruebas-y-datos-de-la-tienda)
12. [Solución de problemas](#-12-solución-de-problemas)
13. [Flujo de trabajo del equipo](#-13-flujo-de-trabajo-del-equipo)
14. [Evidencias de ejecución](#-14-evidencias-de-ejecución)
15. [Próximos pasos](#-15-próximos-pasos)
16. [Equipo y licencia](#-16-equipo-y-licencia)

---

## 📋 1. Descripción general

El sistema está formado por **tres componentes** que se ejecutan como contenedores independientes:

| Componente | Función |
| :--- | :--- |
| **Frontend** (Streamlit) | Interfaz web: inicio de sesión, registro, acceso como invitado y chat. |
| **Backend** (FastAPI) | API REST, autenticación, historial de chat y agente RAG. |
| **Base de datos** (PostgreSQL) | Guarda los usuarios (contraseñas con hash `bcrypt`) y el historial de conversaciones. |

Además depende de un servicio externo: la **API de Google Gemini**, que genera las respuestas.

**Funcionalidades principales**

- Chat con un agente que responde **solo con información de los documentos** de la tienda; si no encuentra la información, lo indica.
- Carga automática de documentos en **8 formatos**: PDF, DOCX, XLSX, PPTX, Markdown, CSV, JSON y HTML.
- **Búsqueda híbrida**: vectorial (FAISS con MMR) + búsqueda por palabras clave normalizadas, con expansión de sinónimos del dominio (por ejemplo, «portátiles» → laptop, notebook; definidos en `backend/utils/text_normalize.py`) y fusión de resultados mediante *Reciprocal Rank Fusion*.
- **Datos oficiales como fuente de verdad:** `datos_oficiales.md` se genera a partir de `config_tienda.json` y `precios_envio.csv` y prevalece sobre cualquier otro documento (ver [`docs/CONTRADICCIONES.md`](docs/CONTRADICCIONES.md) y la [sección 11](#-11-pruebas-y-datos-de-la-tienda)).
- Usuarios corporativos precargados, registro de nuevos usuarios y acceso como invitado.
- Historial de chat persistente por usuario en PostgreSQL.
- El agente responde en la moneda definida por la tienda (COP) y **no realiza conversiones de divisas**.

---

## 🏗️ 2. Arquitectura

```
                  Navegador del usuario
                          │
                          │  http://localhost:8501
                          ▼
             ┌──────────────────────────┐
             │  frontend  (Streamlit)   │   contenedor: agente_frontend
             └────────────┬─────────────┘
                          │  HTTP  ·  BACKEND_URL=http://backend:8000
                          ▼
             ┌──────────────────────────┐
             │  backend  (FastAPI + RAG)│   contenedor: agente_backend  ·  puerto 8000
             │                          │
             │  RAGAgent                │
             │   ├─ búsqueda híbrida    │──────►  FAISS + FastEmbed (local, en disco)
             │   └─ generación          │──────►  Google Gemini (API externa)
             └────────────┬─────────────┘
                          │  SQL (SQLAlchemy + psycopg)
                          ▼
             ┌──────────────────────────┐
             │  db  (PostgreSQL 16)     │   contenedor: agente_db  ·  volumen: pgdata
             └──────────────────────────┘
```

**Flujo de una consulta**

1. El usuario escribe una pregunta en Streamlit, que la envía a `POST /chat` del backend.
2. Si el usuario está autenticado, el backend guarda la pregunta en PostgreSQL.
3. El backend expande la consulta con sinónimos y ejecuta la búsqueda híbrida (vectorial + palabras clave) sobre los documentos indexados.
4. Los fragmentos recuperados se insertan como contexto en el *prompt* y se envían a Gemini.
5. La respuesta se guarda en el historial (usuarios autenticados) y se devuelve al frontend.

**Servicios de `docker-compose.yml`**

| Servicio | Imagen / build | Puerto publicado | Depende de | Persistencia |
| :--- | :--- | :--- | :--- | :--- |
| `db` | `postgres:16-alpine` | — (solo red interna) | — | volumen `pgdata` |
| `backend` | `./backend/Dockerfile` | `8000:8000` | `db` (*healthy*) | volumen `chroma_data` (índice FAISS) |
| `frontend` | `./frontend/Dockerfile` | `8501:8501` | `backend` (*healthy*) | — |

Los tres servicios comparten la red `amershop_net` (tipo *bridge*) y se comunican por nombre de servicio (por ejemplo, el frontend llama a `http://backend:8000`). Los servicios con *healthcheck* (`db` y `backend`) bloquean el arranque del siguiente hasta estar listos. Los contenedores ejecutan el código **empaquetado en la imagen**; no se montan las carpetas del proyecto.

---

## 📁 3. Estructura del repositorio

```
Agente/
├── docker-compose.yml          # Definición de los tres servicios
├── .env.example                # Plantilla de variables de entorno
├── .env                        # Variables reales (NO se sube a Git)
├── README.md
├── .github/
│   ├── CODEOWNERS              # Revisores del repositorio
│   └── PULL_REQUEST_TEMPLATE.md
├── docs/
│   ├── CONTRIBUTION.md         # Guía de contribución (ramas, commits, PR)
│   ├── CONTRADICCIONES.md      # Datos contradictorios y su resolución
│   └── evidencias/             # Capturas de la ejecución
├── backend/
│   ├── Dockerfile
│   ├── main.py                 # API FastAPI y endpoints
│   ├── config.py               # Configuración centralizada
│   ├── db.py                   # Modelos SQLAlchemy y utilidades de contraseñas
│   ├── requirements.txt
│   ├── requirements-dev.txt    # pytest
│   ├── agents/
│   │   ├── rag_agent.py        # Agente RAG (flujo principal)
│   │   └── document_grader.py  # Evaluador de relevancia (disponible, no usado en el flujo principal)
│   ├── loaders/multi_loader.py # Carga de PDF, DOCX, XLSX, PPTX, MD, CSV, JSON, HTML
│   ├── vectorstore/chroma_store.py  # Índice FAISS y búsqueda híbrida
│   ├── utils/text_normalize.py # Normalización, sinónimos y búsqueda por palabras clave
│   ├── scripts/
│   │   ├── generar_datos_oficiales.py  # Genera datos_oficiales.md
│   │   └── auditar_datos.py            # Detecta datos contradictorios en los documentos
│   ├── documents/              # Base de conocimiento de la tienda (ver sección 11)
│   └── tests/                  # Pruebas con pytest
└── frontend/
    ├── Dockerfile
    ├── app.py                  # Interfaz Streamlit
    ├── requirements.txt
    ├── .streamlit/config.toml  # Tema visual
    └── assets/                 # Logo e imágenes
```

---

## 🛠️ 4. Tecnologías

| Categoría | Tecnología | Propósito |
| :--- | :--- | :--- |
| Lenguaje | Python 3.12 | Backend y frontend |
| API | FastAPI + Uvicorn | Endpoints REST |
| Interfaz | Streamlit | Chat y autenticación |
| Orquestación RAG | LangChain | *Prompts*, cadenas y documentos |
| LLM | Google Gemini (`langchain-google-genai`) | Generación de respuestas |
| Embeddings | FastEmbed | Vectorización local de texto |
| Búsqueda vectorial | FAISS (`faiss-cpu`) | Índice con persistencia en disco |
| Base de datos | PostgreSQL 16 + SQLAlchemy + psycopg | Usuarios e historial |
| Seguridad | bcrypt | Hash de contraseñas |
| Contenedores | Docker + Docker Compose | Empaquetado y orquestación |
| Pruebas | pytest | Pruebas automatizadas |

---

## ✅ 5. Requisitos previos

**Para ejecutar con Docker Compose (recomendado)**

- [Docker](https://docs.docker.com/get-docker/) con **Docker Compose v2** (comando `docker compose`). En Windows/macOS basta con **Docker Desktop** abierto y en ejecución.
- [Git](https://git-scm.com/).
- Una **API Key de Google Gemini** gratuita: <https://aistudio.google.com/>
- Conexión a Internet (descarga del modelo de embeddings y llamadas a Gemini).

**Para la instalación tradicional (sin Docker)** se necesita además: Python 3.12 y PostgreSQL 16 instalados en el equipo.

---

## ⚙️ 6. Configuración: variables de entorno

Clona el repositorio y crea el archivo `.env` en la **raíz del proyecto** (puedes partir de `.env.example`):

```bash
git clone https://github.com/Desarrollo-de-software-2-DAM/Agente.git
cd Agente
git checkout develop            # rama de integración del equipo

cp .env.example .env            # Windows (CMD): copy .env.example .env
```

Asegúrate de que el `.env` contenga estas variables (edita los valores marcados):

```env
# --- Google Gemini (OBLIGATORIA) ---
GOOGLE_API_KEY=tu_api_key_aqui

# --- Hugging Face (OPCIONAL: déjalo vacío si no tienes token) ---
HF_TOKEN=

# --- Tienda y modelos ---
STORE_NAME=Amershop
LLM_MODEL_AGENT=gemini-3.8-flash
LLM_MODEL_GRADER=gemini-3.8-flash

# --- Vector store ---
CHROMA_PERSIST_DIR=./chroma_db
COLLECTION_NAME=amershop_docs
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
SEARCH_K=8
DOCUMENTS_DIR=./documents

# --- Contraseñas de los usuarios corporativos (cámbialas) ---
ADMIN_PASSWORD=cambia_esta_clave
USER1_PASSWORD=cambia_esta_clave
USER2_PASSWORD=cambia_esta_clave
RRHH_PASSWORD=cambia_esta_clave
VENTAS_PASSWORD=cambia_esta_clave
SOPORTE_PASSWORD=cambia_esta_clave

# --- Base de datos PostgreSQL ---
POSTGRES_USER=agente
POSTGRES_PASSWORD=cambia_esta_clave
POSTGRES_DB=agente_db
```

| Variable | Obligatoria | Descripción |
| :--- | :---: | :--- |
| `GOOGLE_API_KEY` | ✅ | Clave de la API de Gemini. Sin ella el backend no arranca. |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | ✅ | Credenciales y nombre de la base de datos. Docker Compose las usa para crear PostgreSQL y construir `DATABASE_URL` automáticamente. |
| `ADMIN_PASSWORD`, `USER1_PASSWORD`, `USER2_PASSWORD`, `RRHH_PASSWORD`, `VENTAS_PASSWORD`, `SOPORTE_PASSWORD` | ✅ | Contraseñas de los usuarios precargados (`admin`, `colaborador1`, `colaborador2`, `rrhh`, `ventas`, `soporte`). |
| `LLM_MODEL_AGENT`, `LLM_MODEL_GRADER` | ✅ | Modelo de Gemini usado por el agente y por el evaluador. Debe existir para tu API Key (ver [solución de problemas](#-12-solución-de-problemas)). |
| `SEARCH_K` | ➖ | Número de fragmentos recuperados por consulta (8 por defecto). |
| `DOCUMENTS_DIR` | ➖ | Carpeta con los documentos a indexar (`./documents`). |
| `STORE_NAME` | ➖ | Nombre de la tienda usado en la configuración. |
| `HF_TOKEN` | ➖ | Token de Hugging Face. **Opcional**: el modelo de embeddings es público y se descarga sin token (aparece una advertencia inofensiva). Déjalo vacío si no tienes uno: un valor inválido puede hacer fallar la descarga. |
| `CHROMA_PERSIST_DIR`, `COLLECTION_NAME`, `CHUNK_SIZE`, `CHUNK_OVERLAP` | ➖ | Definidas en `config.py`, pero el código actual usa valores fijos para estos parámetros. Se conservan para configuración futura. |

> ⚠️ **Seguridad:** el archivo `.env` contiene secretos y está en `.gitignore`; **nunca lo subas a GitHub ni lo compartas**. Si una clave se expone, regenérala de inmediato. Las contraseñas del ejemplo son solo de relleno: cámbialas.

---

## 🐳 7. Ejecución con Docker Compose (recomendada)

Con el `.env` listo, desde la raíz del proyecto:

```bash
docker compose up --build
```

Para dejarlo en segundo plano: `docker compose up --build -d`.

**¿Qué ocurre al arrancar?**

1. Se construyen las imágenes del backend y del frontend a partir de sus `Dockerfile`.
2. Se levanta PostgreSQL y Compose espera a que esté **saludable** (`healthcheck`) antes de iniciar el backend.
3. El backend crea las tablas, siembra los usuarios corporativos y, si el índice vectorial está vacío, **indexa los documentos** de `backend/documents/`.
4. Cuando el backend responde (*healthy*), se inicia el frontend.

> ⏳ **El primer arranque es más lento:** se construyen las imágenes, se descarga el modelo de embeddings y se indexan los documentos. Sigue el avance con `docker compose logs -f backend` y espera al mensaje `Application startup complete`. Con las imágenes ya construidas, el sistema queda listo en menos de un minuto. Los arranques siguientes reutilizan el índice guardado en el volumen `chroma_data`.

**Verificar que todo funciona**

```bash
docker compose ps                 # db y backend: "healthy"; frontend: "running"
curl http://localhost:8000/       # → {"status":"ok","message":"Backend de Amershop activo"}
```

| Recurso | URL |
| :--- | :--- |
| Aplicación (frontend) | <http://localhost:8501> |
| API del backend | <http://localhost:8000> |
| Documentación interactiva de la API | <http://localhost:8000/docs> |

**Comandos útiles**

| Acción | Comando |
| :--- | :--- |
| Ver logs de un servicio | `docker compose logs -f backend` |
| Detener (conserva datos) | `docker compose down` |
| Detener y **borrar la base de datos y el índice** | `docker compose down -v` |
| Reconstruir tras cambiar código, documentos, dependencias o `Dockerfile` | `docker compose up --build -d` |
| Reiniciar solo el backend | `docker compose restart backend` |
| Abrir una consola en el backend | `docker compose exec backend bash` |
| Consultar PostgreSQL | `docker compose exec db psql -U agente -d agente_db` |

> ℹ️ **Persistencia:** los usuarios y el historial viven en el volumen `pgdata` y el índice vectorial en `chroma_data`; ambos sobreviven a `docker compose down` y a `restart`. Solo `down -v` los elimina.
>
> **Reindexar tras cambiar los documentos** (`backend/documents/`): los documentos se copian dentro de la imagen y el índice solo se genera cuando está vacío, así que hay que reconstruir y vaciar el índice:
>
> ```bash
> docker compose up --build -d
> docker compose exec backend sh -c "rm -rf /app/chroma_db/*"
> docker compose restart backend
> ```

---

## 💻 8. Instalación tradicional (sin Docker)

Procedimiento para ejecutar los tres componentes directamente en el equipo.

**1. Crear la base de datos en PostgreSQL**

```bash
psql -U postgres
```
```sql
CREATE USER agente WITH PASSWORD 'cambia_esta_clave';
CREATE DATABASE agente_db OWNER agente;
\q
```

**2. Configurar el `.env`** en la raíz (ver [sección 6](#-6-configuración-variables-de-entorno)) y añadir la cadena de conexión, que en modo local apunta a `localhost`:

```env
DATABASE_URL=postgresql+psycopg://agente:cambia_esta_clave@localhost:5432/agente_db
```

> Con Docker Compose esta variable **no** es necesaria: el `docker-compose.yml` la construye solo.

**3. Iniciar el backend** (terminal 1; debe ejecutarse desde la carpeta `backend/`):

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

**4. Iniciar el frontend** (terminal 2):

```bash
cd frontend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py --server.port=8501
```

El frontend se conecta por defecto a `http://localhost:8000` (variable `BACKEND_URL`). Abre <http://localhost:8501>.

---

## 💬 9. Uso de la aplicación

Al abrir la aplicación se ofrecen tres formas de acceso:

- **Iniciar sesión** con un usuario existente.
- **Registrarse** con usuario, correo y contraseña.
- **Acceder como invitado** (el historial no se guarda).

**Usuarios corporativos precargados:** `admin`, `colaborador1`, `colaborador2`, `rrhh`, `ventas` y `soporte`. Sus contraseñas son las definidas en las variables `*_PASSWORD` de tu `.env`.

Los usuarios autenticados conservan su historial de conversaciones en PostgreSQL.

**Preguntas de ejemplo** (las respuestas salen de los documentos de la tienda)

| Pregunta | Respuesta esperada |
| :--- | :--- |
| ¿Cuál es su teléfono? | `+57-800-AMERSHOP` |
| ¿Tienen envío gratuito? | Sí, en compras superiores a `$4.000.000 COP` |
| ¿En qué moneda están los precios? | COP (pesos colombianos); el agente no convierte divisas |
| ¿Cuál es el horario de atención? | Lunes a viernes 09:00–18:00 y sábados 10:00–14:00 |
| ¿Cuál es la política de devoluciones? | 30 días naturales desde la recepción |

Si la pregunta no está relacionada con la tienda o no aparece en los documentos, el agente responde que no encontró información y sugiere consultar con el área correspondiente.

---

## 🔌 10. API del backend

| Método | Endpoint | Descripción |
| :---: | :--- | :--- |
| `GET` | `/` | Comprobación de estado (*health check*). |
| `POST` | `/register` | Registra un usuario (`username`, `email`, `password`). |
| `POST` | `/login` | Valida credenciales (`username`, `password`). |
| `GET` | `/history/{username}` | Devuelve el historial de chat del usuario. |
| `POST` | `/chat` | Envía una pregunta al agente (`prompt`, `chat_history`, `username` opcional). |

Ejemplo:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "¿Cuál es la política de devoluciones?"}'
```

La documentación interactiva (Swagger) está disponible en <http://localhost:8000/docs>.

---

## 🧪 11. Pruebas y datos de la tienda

### Pruebas automatizadas

Las pruebas verifican la normalización y la búsqueda de términos (por ejemplo, que «portátiles» encuentre los *laptops* del catálogo) y la consistencia de los datos entre los documentos.

`pytest` no viene en la imagen de producción; se instala desde `requirements-dev.txt`. Dentro del contenedor en ejecución (necesita Internet):

```bash
docker compose exec backend sh -c "pip install -r requirements-dev.txt && pytest tests -v"
```

O en tu equipo, con el entorno virtual del backend activo:

```bash
cd backend
pip install -r requirements-dev.txt
pytest tests -v
```

> Si reconstruyes la imagen (`up --build`), el contenedor se recrea y `pytest` hay que volver a instalarlo con el mismo comando.

### Fuentes de datos de la tienda

La carpeta `backend/documents/` es la base de conocimiento del agente:

| Archivo | Origen | Contenido |
| :--- | :--- | :--- |
| `config_tienda.json` | **Fuente única de verdad** (manual) | Contacto, horarios, IVA, moneda, pagos, transportistas, umbral de envío gratis y políticas. |
| `precios_envio.csv` | **Fuente única de verdad** (manual) | Tarifas y tiempos de envío por zona y peso. |
| `datos_oficiales.md` | **Generado** — no editar a mano | Resumen consolidado de los dos anteriores; **prevalece** ante cualquier conflicto. |
| `faq.md`, `guia_envios.html`, `politica_privacidad.pdf`, `terminos_condiciones.pdf`, `politica_reembolso.docx`, `presentacion_empresa.pptx` | Manual | Documentos de apoyo; deben coincidir con los datos oficiales. |
| `catalogo_productos.xlsx` | Manual | Catálogo; se indexa una ficha por producto. |

### Cambiar los datos de la tienda

Si modificas `config_tienda.json` o `precios_envio.csv`, hay que regenerar `datos_oficiales.md` y reindexar. Como el código corre dentro de la imagen, se hace con el contenedor:

```bash
docker compose up --build -d      # la imagen debe contener tus cambios
docker compose exec backend python scripts/generar_datos_oficiales.py
docker cp agente_backend:/app/documents/datos_oficiales.md backend/documents/datos_oficiales.md
docker compose up --build -d      # reconstruye con el archivo regenerado
docker compose exec backend sh -c "rm -rf /app/chroma_db/*"
docker compose restart backend
```

> Si tienes Python y `pandas` instalados en tu equipo, puedes ejecutar `python backend/scripts/generar_datos_oficiales.py` directamente y omitir el `docker cp`.

Cambios en los documentos manuales (`faq.md`, PDF, etc.) solo requieren reconstruir y reindexar (último bloque de la [sección 7](#-7-ejecución-con-docker-compose-recomendada)).

### Auditar contradicciones

`auditar_datos.py` lee los documentos tal como los ve el agente y busca términos que contradicen la configuración regional (COP, `+57`, IVA 19 %, nombre «Amershop»): notación científica en cifras, `USD`/`MXN`, `+52`, `SPEI`/`OXXO`, `Estafeta`, `AmershOp`, etc.

```bash
docker compose exec backend python scripts/auditar_datos.py
```

Termina con código 1 si encuentra algo. Algunos hallazgos pueden ser legítimos (por ejemplo, un método de pago como PayPal que la tienda sí acepta); se listan para revisión manual. Ejecútalo después de cualquier cambio en los documentos, junto con `pytest`.

---

## 🩺 12. Solución de problemas

| Síntoma | Causa probable | Solución |
| :--- | :--- | :--- |
| El backend se detiene con `API Key de Google no configurada` | `GOOGLE_API_KEY` vacía o ausente en el `.env`. | Define la variable y ejecuta `docker compose up -d --force-recreate backend`. |
| El frontend muestra «No se pudo conectar con el servicio Backend» | El backend aún está iniciando (descarga de modelo e indexación) o se detuvo. | Revisa `docker compose logs -f backend` y espera a `Application startup complete`. |
| Error de modelo no encontrado / no soportado al preguntar | El nombre en `LLM_MODEL_AGENT` no está disponible para tu API Key. | Lista los modelos válidos con `docker compose exec backend python test_modelos.py`, copia uno al `.env` y reinicia el backend. |
| El agente responde «No encontré información…» sobre algo que sí está en los documentos | La búsqueda no recuperó el fragmento (por ejemplo, un sinónimo mal definido que desvía la consulta). | Revisa en `docker compose logs backend` la línea `Búsqueda híbrida: '…' -> '…'`, que muestra cómo se expandió la pregunta, y ajusta los sinónimos en `backend/utils/text_normalize.py`. |
| Las respuestas no reflejan documentos actualizados | La imagen o el índice vectorial guardado son antiguos. | Sigue el procedimiento de reindexado de la [sección 7](#-7-ejecución-con-docker-compose-recomendada). |
| `pytest: executable file not found` | `pytest` no está en la imagen (o se reconstruyó). | Usa el comando completo de la [sección 11](#-11-pruebas-y-datos-de-la-tienda), que lo instala antes. |
| `can't open file '/app/scripts/auditar_datos.py'` | El archivo no está en `backend/scripts/` o no reconstruiste la imagen. | Copia el archivo a `backend/scripts/` y ejecuta `docker compose up --build -d`. |
| `password authentication failed for user "agente"` | Cambiaste `POSTGRES_PASSWORD` pero el volumen `pgdata` conserva la contraseña anterior. | `docker compose down -v` (**borra los datos**) y vuelve a levantar. |
| `port is already allocated` (8000 / 8501) | Otro programa usa ese puerto. | Cierra el otro programa o cambia el puerto publicado en `docker-compose.yml`. |
| `docker compose ps` muestra una imagen `sha256:…` en lugar de su nombre | La imagen se reconstruyó pero el contenedor no se recreó. | `docker compose up -d --force-recreate frontend` (o el servicio afectado). |
| `Cannot connect to the Docker daemon` | Docker no está en ejecución. | Abre Docker Desktop (o inicia el servicio `docker`). |
| Advertencia `You are sending unauthenticated requests to the HF Hub` | `HF_TOKEN` está vacío. | Es inofensiva: el modelo se descarga igual. Para quitarla, crea un token gratuito en <https://huggingface.co/settings/tokens> y ponlo en `HF_TOKEN`. |
| Error `401` al descargar el modelo de embeddings | `HF_TOKEN` tiene un valor inválido (por ejemplo, texto de relleno). | Déjalo vacío o usa un token válido y reinicia con `docker compose up -d --force-recreate backend`. |

---

## 🤝 13. Flujo de trabajo del equipo

El detalle completo está en [`docs/CONTRIBUTION.md`](docs/CONTRIBUTION.md). Resumen:

- **Ramas:** la rama principal se mantiene estable; el trabajo se integra en `develop` y cada tarea se desarrolla en una rama `feature/nombre-de-la-tarea`. **No se hace *push* directo a `develop`.**
- **Commits:** mensajes con prefijo — `feat` (nueva funcionalidad), `fix` (corrección), `test` (pruebas) y `docs` (documentación).
- **Pull Requests:** siempre hacia `develop`, usando la [plantilla de PR](.github/PULL_REQUEST_TEMPLATE.md), con un revisor asignado e imágenes de prueba como evidencia.
- **Revisores:** definidos en [`.github/CODEOWNERS`](.github/CODEOWNERS).
- **Gestión de tareas:** [Tablero de Trello del proyecto](https://trello.com/b/INnd5tDp/devops-agente-ia-corporativo).

---

## 📸 14. Evidencias de ejecución

Las capturas de la aplicación ejecutándose con Docker Compose (construcción de imágenes, `docker compose ps`, pruebas, aplicación en el navegador y documentación de la API) se encuentran en la carpeta [`docs/evidencias/`](docs/evidencias/).

<!--
Cuando tengas las capturas en docs/evidencias/, descomenta y ajusta los nombres:

![docker compose up](docs/evidencias/01_compose_up.png)
![docker compose ps](docs/evidencias/02_compose_ps.png)
![Aplicación en el navegador](docs/evidencias/03_app_chat.png)
![API /docs](docs/evidencias/04_api_docs.png)
![pytest](docs/evidencias/05_pytest.png)
-->

---

## 🚀 15. Próximos pasos

La segunda entrega del proyecto incorporará **integración y entrega continua (CI/CD)**: un servidor Jenkins en la nube conectado a GitHub mediante *webhook*, con un *pipeline* de *checkout → build → test → docker build → delivery* que despliegue la aplicación con Docker Compose.

---

## 🛡️ 16. Equipo y licencia

Desarrollado por el equipo del curso **Desarrollo de Software II**: [@Amerx12](https://github.com/Amerx12), [@andres150921](https://github.com/andres150921) y [@DanielJH414](https://github.com/DanielJH414).

Proyecto académico para **Amershop** — Plataforma Corporativa de IA. Todos los derechos reservados.
