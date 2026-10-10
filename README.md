# 🛒 Amershop — Agente IA Corporativo

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.2+-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![Cohere](https://img.shields.io/badge/Agent-cohere-F55036?style=for-the-badge&logo=cohere&logoColor=white)
![Oracle_Cloud](https://img.shields.io/badge/Oracle_Cloud-OCI-F80000?style=for-the-badge&logo=oracle&logoColor=white)

**Asistente virtual inteligente de atención y consulta corporativa para la tienda de tecnología Amershop.**

</div>

---

## 📸 Capturas de Pantalla y Evidencia Visual

![Pantalla de Login - Parte Superior](./assets/demo_login_top.png)

---

![Pantalla de Login - Opciones y GIS](./assets/demo_login_bottom.png)

---

## 📋 1. Descripción General del Proyecto

**Amershop IA** es una plataforma corporativa de asistencia inteligente basada en una arquitectura **RAG (Retrieval-Augmented Generation)**. Su propósito principal es brindar soporte instantáneo, preciso y fundamentado a colaboradores y clientes sobre las políticas internas, envíos, métodos de pago, devoluciones y catálogo de productos de la tienda online de tecnología Amershop.

---

## 🏗️ 2. Arquitectura de la Solución Implementada

La solución sigue un patrón RAG desacoplado de 3 capas: **Frontend**, **Agente RAG / Pipeline LLM** y **Vector Store / Ingesta de Documentos**.

```
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACIÓN                     │
│               Streamlit UI (Tema Glassmorphism)             │
│   ┌──────────────────┐ ┌──────────────────┐ ┌────────────┐   │
│   │ Login (GIS/User) │ │ Cartel LED 24/7  │ │ Chat Canvas│   │
│   └────────┬─────────┘ └──────────────────┘ └─────┬──────┘   │
└────────────┼──────────────────────────────────────┼─────────┘
             │                                      │
             ▼                                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE LÓGICA / RAG                     │
│                 LangChain + Groq LLM Chain                  │
│   ┌─────────────────────────────────────────────────────┐   │
│   │ RAGAgent: Búsqueda MMR k=5 -> Document Grader      │   │
│   │ Prompt Template Estricto (Restricción USD + No invento)│  │
│   └──────────────────────────┬──────────────────────────┘   │
└──────────────────────────────┼──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 CAPA DE DATOS Y VECTORES                    │
│             VectorStoreManager (FAISS / Chroma)             │
│   ┌──────────────────────┐      ┌───────────────────────┐   │
│   │ Base Vectorial FAISS │      │ Loaders Multiformato  │   │
│   │ SentenceTransformers │      │ PDF, DOCX, XLSX, HTML │   │
│   └──────────────────────┘      └───────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ 3. Tecnologías y Herramientas Utilizadas

| Categoría | Tecnología / Herramienta | Propósito / Función |
| :--- | :--- | :--- |
| **Lenguaje Base** | Python 3.11+ | Entorno de desarrollo principal |
| **LLM Engine** | Groq (`llama-3.1-8b-instant`) | Generación rápida de respuestas |
| **Embeddings** | HuggingFace (`all-MiniLM-L6-v2`) | Conversión vectorial de texto |
| **Orquestación RAG** | LangChain Core & Groq Integration | Pipeline RAG, Prompts y Chains |
| **Vector DB** | FAISS / ChromaDB | Almacenamiento vectorial y búsqueda MMR |
| **Frontend Web** | Streamlit 1.35+ | Interfaz gráfica interactiva y reactiva |
| **Autenticación** | Google Identity Services (GIS) | SDK oficial de inicio de sesión con Google |
| **Despliegue Cloud** | Oracle Cloud Infrastructure (OCI) | VM Always Free Ubuntu 22.04 LTS |

---

## 🚀 4. Instrucciones para Ejecutar el Proyecto y Despliegue Cloud

### Opción A: Ejecución Local

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/TU_USUARIO/agente.git
   cd agente
   ```

2. **Crear entorno virtual e instalar dependencias:**
   ```bash
   python -m venv venv
   # En Windows:
   .\venv\Scripts\activate
   # En Linux/macOS:
   source venv/bin/activate

   pip install -r requirements.txt
   ```

3. **Configurar el archivo de entorno (`.env`):**
   Crea un archivo `.env` en la raíz del proyecto basándote en `.env.example`:
   ```env
   GROQ_API_KEY=tu_api_key_de_groq_aqui
   GOOGLE_CLIENT_ID=tu_client_id_de_google_opcional
   ```

4. **Iniciar la aplicación:**
   ```bash
   streamlit run app.py
   ```
   Abre tu navegador en [http://localhost:8501](http://localhost:8501).

---

### Opción B: Despliegue en la Nube (Oracle Cloud OCI - Always Free)

1. **Crear VM en Oracle Cloud:**
   - Instancia: Ubuntu 22.04 LTS (Shape `VM.Standard.E2.1.Micro` o `A1.Flex`).
   - Abre el puerto `8501` en las reglas de entrada del VCN (Ingress Rules: TCP `8501`).

![Configuración de Reglas de Entrada (Ingress Rules) en Oracle Cloud OCI](./assets/demo_oracle_ingress.png)

2. **Configurar el Servidor Linux (SSH) e Iniciar Servicio:**
   ```bash
   sudo apt update && sudo apt install python3-pip git -y
   git clone https://github.com/TU_USUARIO/agente.git
   cd agente
   pip3 install -r requirements.txt
   nano .env # (Inserta tu GROQ_API_KEY)
   ```

3. **Habilitar el puerto en el firewall de Ubuntu y ejecutar:**
   ```bash
   sudo iptables -F
   sudo iptables -P INPUT ACCEPT
   nohup python3 -m streamlit run app.py --server.port 8501 --server.headless true &
   ```

![Ejecución del servicio Streamlit y verificación de IP en Terminal OCI](./assets/demo_deploy_terminal.png)

---

## ❓ 5. Ejemplos de Preguntas y Respuestas que el Agente Puede Responder

![Ejemplo de Preguntas Frecuentes Sugeridas e Interfaz de Inicio de Chat](./assets/ejemplo_preguntas_1.png)

---

![Ejemplo de Respuestas Generadas - Moneda y Catálogo](./assets/ejemplo_respuestas_1.png)

---

![Ejemplo de Respuestas Generadas - Horario de Atención](./assets/ejemplo_respuestas_2.png)

---

## 🛡️ Licencia y Créditos
Desarrollado para **Amershop** — Plataforma Corporativa de IA. Todos los derechos reservados.
