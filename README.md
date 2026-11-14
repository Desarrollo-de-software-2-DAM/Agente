# Amershop — Agente IA Corporativo

Aplicación web para consultar información de la tienda tecnológica **Amershop** sobre productos, envíos, devoluciones, garantías, medios de pago y políticas internas. El asistente utiliza una arquitectura RAG (*Retrieval-Augmented Generation*): recupera fragmentos de los documentos de la tienda y los utiliza como contexto para generar respuestas.

En la configuración predeterminada, la generación de respuestas se realiza localmente mediante **Ollama**. No requiere una API Key de Gemini ni consume tokens de un servicio de IA externo para generar respuestas. Se necesita conexión a Internet durante la instalación para descargar imágenes, dependencias, el modelo y, cuando corresponda, el modelo de embeddings.

> Proyecto académico de **Desarrollo de Software II**. Esta documentación describe la preparación y ejecución del proyecto con Docker y Docker Compose, correspondiente a la primera entrega. La automatización CI/CD con Jenkins corresponde a la segunda entrega.

---

## Contenido

1. [Descripción y funcionalidades](#1-descripción-y-funcionalidades)
2. [Tecnologías](#2-tecnologías)
3. [Arquitectura](#3-arquitectura)
4. [Estructura del repositorio](#4-estructura-del-repositorio)
5. [Requisitos previos](#5-requisitos-previos)
6. [Configuración de variables de entorno](#6-configuración-de-variables-de-entorno)
7. [Instalación y ejecución con Docker Compose](#7-instalación-y-ejecución-con-docker-compose)
8. [Uso de la aplicación](#8-uso-de-la-aplicación)
9. [API del backend](#9-api-del-backend)
10. [Pruebas automatizadas](#10-pruebas-automatizadas)
11. [Instalación tradicional sin Docker](#11-instalación-tradicional-sin-docker)
12. [Administración y solución de problemas](#12-administración-y-solución-de-problemas)
13. [Documentación y evidencias](#13-documentación-y-evidencias)
14. [Flujo de trabajo del equipo](#14-flujo-de-trabajo-del-equipo)
15. [Alcance de las entregas](#15-alcance-de-las-entregas)
16. [Equipo](#16-equipo)

---

## 1. Descripción y funcionalidades

Amershop ofrece una interfaz web que permite:

- Consultar información de productos y del catálogo.
- Consultar políticas de envíos, devoluciones, garantías, pagos y atención.
- Realizar consultas en lenguaje natural al agente RAG.
- Registrarse e iniciar sesión.
- Acceder como invitado; las conversaciones de invitado no se asocian a un usuario persistente.
- Recuperar el historial de conversaciones de usuarios registrados.
- Consultar el estado de los servicios desde la landing page.

El sistema incluye normalización de consultas y búsqueda híbrida: recuperación vectorial con FAISS y búsqueda léxica basada en términos normalizados y sinónimos. La respuesta del agente utiliza los documentos recuperados como contexto; la calidad y precisión dependen de la vigencia y consistencia de esos documentos.

## 2. Tecnologías

| Área | Tecnología | Uso |
|---|---|---|
| Lenguaje | Python 3.12 | Backend y frontend |
| Interfaz web | Streamlit | Landing page, autenticación y chat |
| API | FastAPI + Uvicorn | Servicios REST |
| Orquestación RAG | LangChain | Prompts y cadena de generación |
| Modelo local | Ollama | Generación de respuestas |
| Embeddings | FastEmbed | Representación vectorial de documentos |
| Búsqueda vectorial | FAISS (`faiss-cpu`) | Índice y recuperación vectorial |
| Base de datos relacional | PostgreSQL 16, SQLAlchemy y psycopg | Usuarios e historial |
| Alternativa local de BD | SQLite | Ejecución local cuando no se define `DATABASE_URL` |
| Contraseñas | bcrypt | Hash de contraseñas almacenadas |
| Contenedores | Docker y Docker Compose | Construcción y orquestación |
| Pruebas | pytest, pytest-asyncio y HTTPX | Validación automatizada |

## 3. Arquitectura

```text
Navegador
   |
   v
Frontend: Streamlit (8501)
   |
   | HTTP interno: http://backend:8000
   v
Backend: FastAPI (8000)
   |                 |                  |
   | SQL             | búsqueda         | generación
   v                 v                  v
PostgreSQL       FAISS + FastEmbed    Ollama
(usuarios e      (índice y            (modelo local)
 historial)       documentos)
```

### Servicios definidos en Docker Compose

| Servicio | Imagen / construcción | Función | Puerto publicado |
|---|---|---|---|
| `db` | `postgres:16-alpine` | Usuarios e historial | No se publica al host; solo red interna |
| `ollama` | `ollama/ollama:latest` | Servicio de modelos locales | `127.0.0.1:11434` |
| `ollama-pull` | `curlimages/curl:latest` | Descarga el modelo configurado y finaliza | No aplica |
| `backend` | `backend/Dockerfile` | API, lógica RAG y persistencia | `8000:8000` |
| `frontend` | `frontend/Dockerfile` | Interfaz Streamlit | `8501:8501` |

`ollama-pull` es un servicio auxiliar de una sola ejecución. Por eso, que su estado aparezca como `Exited` después de una descarga correcta es esperado; se debe comprobar que terminó con código de salida cero y que el backend está saludable.

### Redes y volúmenes

- Red `amershop_net` tipo `bridge` para la comunicación entre servicios.
- Volumen `pgdata` para los datos de PostgreSQL.
- Volumen `ollama_data` para los modelos descargados de Ollama.
- Compose declara `faiss_data` montado en `/app/faiss_db`. **Nota de revisión:** el `VectorStoreManager` de la versión revisada utiliza por defecto `./faiss_db/` (dentro del contenedor: `/app/faiss_db`) y no recibe actualmente `FAISS_PERSIST_DIR`. Por tanto, el volumen `faiss_data` no respalda el índice activo hasta que se alinee la configuración del código o el punto de montaje. No debe afirmarse que el índice FAISS persiste en ese volumen antes de corregir y validar este detalle.

## 4. Estructura del repositorio

```text
Agente/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README.md
├── iniciar_local.bat
├── iniciar_local.ps1
├── iniciar_local.sh
├── .github/
│   ├── CODEOWNERS
│   └── PULL_REQUEST_TEMPLATE.md
├── backend/
│   ├── Dockerfile
│   ├── pytest.ini                 # Configuración de pytest en la copia local
│   ├── config.py
│   ├── db.py
│   ├── main.py
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── agents/
│   ├── documents/
│   ├── loaders/
│   ├── scripts/
│   ├── tests/
│   ├── utils/
│   └── vectorstore/
│       └── chroma_store.py        # Gestor FAISS (el nombre histórico contiene “chroma”)
├── frontend/
│   ├── Dockerfile
│   ├── app.py
│   ├── landing.py
│   ├── requirements.txt
│   ├── .streamlit/
│   └── assets/
└── docs/
    ├── CONTRIBUTION.md
    ├── CONTRADICCIONES.md
    ├── DEPLOY_VPS.md
    └── evidencias/
        ├── README.md
        ├── ChatAgente.png
        ├── Docker_compose_ps.png
        ├── Docker_compose_up.png
        ├── Docker_pytest.png
        └── Login.png
```

La estructura anterior representa los directorios y archivos principales. Los scripts de inicio local son auxiliares; para la ejecución reproducible de la entrega se recomienda Docker Compose.

## 5. Requisitos previos

### Ejecución recomendada con Docker

- Git.
- Docker Desktop en Windows/macOS o Docker Engine en Linux.
- Docker Compose v2 (`docker compose`, con espacio).
- Docker en ejecución antes de lanzar los comandos.
- Conexión a Internet para descargar imágenes, dependencias, el modelo de Ollama y los embeddings cuando sea necesario.
- Memoria y espacio en disco suficientes para las imágenes, el modelo seleccionado, los documentos y el índice. El consumo real depende del modelo de Ollama y del tamaño de la base documental.

### Ejecución tradicional

- Python 3.12.
- Ollama instalado y ejecutándose en el equipo.
- El modelo configurado descargado en Ollama.
- PostgreSQL 16 solo si se desea usar PostgreSQL localmente. Si no se define `DATABASE_URL`, el backend usa SQLite local automáticamente.

## 6. Configuración de variables de entorno

Desde la raíz del repositorio, crear `.env` a partir de `.env.example`:

**Windows PowerShell**

```powershell
Copy-Item .env.example .env
```

**Linux/macOS**

```bash
cp .env.example .env
```

Editar `.env` antes de iniciar el sistema. La configuración predeterminada usa Ollama:

```env
STORE_NAME=Amershop
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2
OLLAMA_TEMPERATURE=0.1

POSTGRES_USER=agente
POSTGRES_PASSWORD=reemplazar_por_una_clave_segura
POSTGRES_DB=agente_db

ADMIN_PASSWORD=reemplazar
USER1_PASSWORD=reemplazar
USER2_PASSWORD=reemplazar
RRHH_PASSWORD=reemplazar
VENTAS_PASSWORD=reemplazar
SOPORTE_PASSWORD=reemplazar

HF_TOKEN=
GOOGLE_API_KEY=
```

### Variables principales

| Variable | Uso | Observaciones |
|---|---|---|
| `STORE_NAME` | Nombre de la tienda | Predeterminado: `Amershop` |
| `LLM_PROVIDER` | Proveedor de generación | `ollama` es el predeterminado; `gemini` requiere `GOOGLE_API_KEY` |
| `OLLAMA_BASE_URL` | Dirección de Ollama | En Compose: `http://ollama:11434`; fuera de Docker: normalmente `http://localhost:11434` |
| `OLLAMA_MODEL` | Modelo de Ollama | Predeterminado: `llama3.2` |
| `OLLAMA_TEMPERATURE` | Temperatura de generación | Predeterminado: `0.1` |
| `GOOGLE_API_KEY` | Clave para proveedor Gemini | No es necesaria con `LLM_PROVIDER=ollama` |
| `LLM_MODEL_AGENT`, `LLM_MODEL_GRADER` | Modelos Gemini | Solo se utilizan al configurar el proveedor Gemini y los componentes correspondientes |
| `HF_TOKEN` | Token opcional de Hugging Face | Puede permanecer vacío para modelos públicos compatibles |
| `POSTGRES_USER` | Usuario PostgreSQL | Compose lo utiliza para iniciar la BD |
| `POSTGRES_PASSWORD` | Contraseña PostgreSQL | Debe cambiarse antes de exponer el servicio |
| `POSTGRES_DB` | Nombre de BD | Predeterminado: `agente_db` |
| `ADMIN_PASSWORD`, `USER1_PASSWORD`, `USER2_PASSWORD`, `RRHH_PASSWORD`, `VENTAS_PASSWORD`, `SOPORTE_PASSWORD` | Contraseñas iniciales | Cambiar los valores antes de un despliegue compartido |
| `FAISS_PERSIST_DIR` | Ruta configurada para el índice | En la versión revisada aparece en configuración, pero el gestor vectorial usa por defecto `./faiss_db/`; alinear código y volumen antes de confiar en esta variable |

> **Seguridad:** `.env` contiene credenciales y no debe subirse al repositorio. `.env.example` es solo una plantilla. No reutilizar las contraseñas de ejemplo en un entorno compartido o de producción.

## 7. Instalación y ejecución con Docker Compose

### 7.1 Clonar el repositorio

```bash
git clone https://github.com/Desarrollo-de-software-2-DAM/Agente.git
cd Agente
git switch develop
git pull origin develop
```

Si el equipo entrega una rama específica para revisión, cambiar a esa rama en lugar de `develop`.

### 7.2 Crear y revisar `.env`

Ejecutar los pasos de la [sección 6](#6-configuración-de-variables-de-entorno). Confirmar que el archivo `.env` está en la raíz, junto a `docker-compose.yml`.

### 7.3 Construir e iniciar los servicios

```bash
docker compose up -d --build
```

El arranque sigue estas dependencias:

1. PostgreSQL inicia y ejecuta su comprobación de salud.
2. Ollama inicia y espera estar disponible.
3. `ollama-pull` solicita a Ollama la descarga del modelo configurado y termina cuando la descarga concluye.
4. El backend inicia después de que PostgreSQL esté saludable y `ollama-pull` haya terminado correctamente.
5. El frontend inicia cuando el backend está saludable.

La primera ejecución puede tardar más debido a la descarga de imágenes, paquetes, modelo e embeddings, además de la indexación documental.

### 7.4 Comprobar el estado

```bash
docker compose ps
```

Estados esperados: `db`, `ollama`, `backend` y `frontend` en ejecución y saludables cuando terminen sus comprobaciones. `ollama-pull` puede aparecer como `Exited` después de finalizar correctamente.

Consultar logs:

```bash
docker compose logs --tail=100 backend
docker compose logs --tail=100 frontend
docker compose logs --tail=100 ollama
docker compose logs --tail=100 ollama-pull
```

### 7.5 Direcciones locales

| Recurso | Dirección |
|---|---|
| Landing page y chat | <http://localhost:8501> |
| API FastAPI | <http://localhost:8000> |
| Swagger UI | <http://localhost:8000/docs> |
| Estado detallado | <http://localhost:8000/status> |

### 7.6 Detener y administrar

```bash
# Detener y eliminar contenedores, conservando volúmenes
docker compose down

# Iniciar de nuevo
docker compose up -d

# Reconstruir imágenes después de modificar código o dependencias
docker compose up -d --build

# Ver estado
docker compose ps

# Seguir logs del backend
docker compose logs -f backend

# Abrir una terminal en el backend
docker compose exec backend sh
```

> `docker compose down -v` elimina también los volúmenes declarados y, por tanto, puede borrar los datos de PostgreSQL y los modelos descargados. Usarlo solo cuando se desee reiniciar esos datos y exista una copia de seguridad si es necesaria.

## 8. Uso de la aplicación

1. Abrir <http://localhost:8501>.
2. Desde la landing page, elegir ingresar, registrarse o continuar como invitado.
3. Enviar preguntas relacionadas con los productos y políticas de Amershop.
4. Los usuarios autenticados pueden consultar su historial; el modo invitado no lo persiste asociado a una cuenta.
5. Consultar el estado del backend y del modelo desde la sección de indicadores de la landing page.

Preguntas de prueba que se pueden utilizar (la respuesta concreta depende del contenido vigente de `backend/documents/`):

- ¿Cuál es la política de devoluciones?
- ¿Tienen envío gratuito?
- ¿En qué moneda están los precios?
- ¿Cuál es el horario de atención?
- ¿Qué medios de pago acepta la tienda?

## 9. API del backend

Los endpoints observados en `backend/main.py` son:

| Método | Ruta | Función |
|---|---|---|
| `GET` | `/` | Comprobación general del backend |
| `GET` | `/status` | Estado detallado, conexión a BD, proveedor LLM, usuarios, mensajes y documentos indexados |
| `POST` | `/register` | Registro de usuario (`username`, `email`, `password`) |
| `POST` | `/login` | Validación de credenciales (`username`, `password`) |
| `GET` | `/history/{username}` | Consulta de historial de un usuario |
| `POST` | `/chat` | Consulta al agente (`prompt`, `chat_history` y `username` opcional) |
| `GET` | `/docs` | Documentación Swagger UI generada por FastAPI |

Ejemplo de consulta:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"¿Cuál es la política de devoluciones?","chat_history":[]}'
```

La definición interactiva se encuentra en <http://localhost:8000/docs>.

> **Alcance de seguridad:** el backend verifica credenciales y almacena contraseñas mediante bcrypt, pero la implementación revisada no utiliza tokens de sesión/JWT para proteger los endpoints de historial y chat. No debe presentarse como un sistema de autenticación de producción sin una revisión y un refuerzo adicional de autorización.

## 10. Pruebas automatizadas

Las pruebas se encuentran en `backend/tests/`. El archivo `backend/pytest.ini` limita la recopilación al directorio `tests` y a los archivos `test_*.py`.

Ejecutar dentro del backend en Docker:

```bash
docker compose exec backend pytest -q
```

Para ver cada prueba:

```bash
docker compose exec backend pytest tests -v
```

La suite cubre, entre otros aspectos, endpoints de la API, registro e inicio de sesión, historial, ingesta de documentos, normalización/búsqueda y comportamiento del agente RAG con un modelo simulado.

**Validación realizada en el entorno local del equipo el 13 de noviembre de 2026:** `40 passed, 3 warnings`. Los avisos correspondieron a advertencias de obsolescencia de `pytest-asyncio`, integración de embeddings de `langchain-community` y eventos de inicio de FastAPI; no fueron fallos de pruebas. Este resultado debe acompañarse de la captura actualizada en `docs/evidencias/` y mantenerse sincronizado con los cambios que finalmente se suban a GitHub.

## 11. Instalación tradicional sin Docker

Esta modalidad ejecuta backend y frontend directamente en el equipo. Requiere Python 3.12 y un servicio Ollama local. PostgreSQL es opcional porque `backend/db.py` utiliza SQLite cuando no se configura `DATABASE_URL`.

### 11.1 Preparar Ollama

Instalar Ollama siguiendo las instrucciones oficiales para el sistema operativo. Asegurarse de que el servicio esté activo y descargar el modelo configurado, por ejemplo:

```bash
ollama pull llama3.2
```

### 11.2 Configurar variables

Crear `.env` en la raíz del proyecto. Para ejecución fuera de Docker, cambiar:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

Si se usará PostgreSQL local, definir `DATABASE_URL` con la dirección, usuario, contraseña y base de datos correspondientes. Si se omite, se utilizará SQLite en `backend/agente_amershop.db`.

### 11.3 Instalar e iniciar backend

En una terminal:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

En Linux/macOS, activar el entorno con:

```bash
source .venv/bin/activate
```

### 11.4 Instalar e iniciar frontend

En otra terminal, desde la raíz del repositorio:

```powershell
cd frontend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m streamlit run app.py --server.port 8501
```

Abrir <http://localhost:8501>. El frontend usa `BACKEND_URL` y, en ejecución local, debe apuntar a `http://localhost:8000`.

> Los scripts `iniciar_local.bat`, `iniciar_local.ps1` e `iniciar_local.sh` son auxiliares. La instalación manual anterior deja explícitos los pasos de creación de entornos e instalación de dependencias.

## 12. Administración y solución de problemas

| Síntoma | Comprobación o solución |
|---|---|
| `env file .env not found` | Crear `.env` en la raíz con una copia de `.env.example`. |
| Docker no conecta | Abrir Docker Desktop o iniciar el servicio Docker y volver a ejecutar `docker compose ps`. |
| Frontend no conecta al backend | Revisar `docker compose ps` y `docker compose logs --tail=100 backend frontend`. Esperar a que el backend finalice el inicio. |
| Ollama no responde | Revisar `docker compose logs ollama ollama-pull`; comprobar que el modelo configurado se descargó correctamente. |
| Modelo no encontrado | Ejecutar `docker compose exec ollama ollama list`. Si falta, descargarlo con `docker compose exec ollama ollama pull llama3.2` (sustituir por el valor real de `OLLAMA_MODEL`). |
| Puerto 8000 o 8501 ocupado | Cerrar el proceso que utiliza el puerto o cambiar la publicación correspondiente en `docker-compose.yml`. |
| Contraseña PostgreSQL rechazada después de cambiar `.env` | El volumen existente puede conservar las credenciales iniciales. No ejecutar `down -v` sin confirmar que se pueden borrar los datos. Realizar respaldo y planificar la recreación de la BD. |
| Cambios documentales no aparecen en el agente | Reconstruir la imagen si los documentos se copian durante el build y revisar el procedimiento de reindexación. Ver la nota de ruta del índice en la sección 3 antes de borrar datos. |
| `pytest` no encuentra pruebas | Ejecutar `docker compose exec backend pytest -q` desde la raíz del proyecto y verificar que `backend/pytest.ini` exista en la imagen reconstruida. |

## 13. Documentación y evidencias

- [Guía de despliegue en VPS](docs/DEPLOY_VPS.md)
- [Flujo de contribución](docs/CONTRIBUTION.md)
- [Registro de contradicciones de datos](docs/CONTRADICCIONES.md)
- [Índice de evidencias](docs/evidencias/README.md)

La carpeta `docs/evidencias/` reúne capturas de construcción, estado de contenedores, pruebas y funcionamiento de la interfaz. Las capturas de pruebas deben corresponder a la versión final que se entrega.

## 14. Flujo de trabajo del equipo

La rama `develop` es la rama de integración. Las tareas se desarrollan en ramas independientes y se integran mediante Pull Request hacia `develop`. No realizar `push` directo a la rama de integración.

Consultar [docs/CONTRIBUTION.md](docs/CONTRIBUTION.md) para los comandos y reglas de commits, revisión y evidencias en Pull Requests.

## 15. Alcance de las entregas

**Primera entrega:** preparación del proyecto, organización del repositorio, Dockerfiles, variables de entorno, Docker Compose, aplicación ejecutándose, documentación técnica y evidencias.

**Segunda entrega:** servidor CI/CD, conexión automatizada con el repositorio, pipeline de checkout/build/test/docker build/delivery y despliegue automatizado. Estos elementos no se presentan como completados en esta documentación de la primera entrega.

## 16. Equipo

Proyecto académico desarrollado para el curso **Desarrollo de Software II** por:

- [@Amerx12](https://github.com/Amerx12)
- [@andres150921](https://github.com/andres150921)
- [@DanielJH414](https://github.com/DanielJH414)

Proyecto: **Amershop — Agente IA Corporativo**.
