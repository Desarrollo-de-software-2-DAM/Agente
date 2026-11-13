"""
Amershop — Landing Page Principal
Página interactiva y moderna que conecta todos los componentes del sistema.
"""

import os
import requests
import streamlit as st
from pathlib import Path

# Obtener URL del backend
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
_assets_dir = Path(__file__).resolve().parent / "assets"
LOGO_PATH = str(_assets_dir / "logo.jpg")


def get_backend_status():
    """Consulta el estado del backend y la base de datos."""
    try:
        res = requests.get(f"{BACKEND_URL}/status", timeout=3)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    try:
        # Fallback al endpoint raíz
        res = requests.get(f"{BACKEND_URL}/", timeout=3)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None


def render_landing_page():
    """Renderiza la Landing Page completa de Amershop."""

    status = get_backend_status()
    is_online = status is not None
    doc_count = status.get("documents_indexed", 0) if status else 0
    model_name = status.get("llm_model") or status.get("model") or "llama3.2 (Local)"
    provider = status.get("llm_provider", "ollama")

    # -------------------------------------------------------------
    # HERO SECTION
    # -------------------------------------------------------------
    st.markdown("""
        <div style="
            text-align: center;
            padding: 40px 20px 30px 20px;
            background: radial-gradient(circle at 50% 20%, rgba(138, 43, 226, 0.25) 0%, rgba(15, 12, 28, 0.9) 70%);
            border-radius: 20px;
            border: 1px solid rgba(138, 43, 226, 0.3);
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        ">
            <span style="
                background: linear-gradient(90deg, #8a2be2, #4a00e0);
                color: #ffffff;
                padding: 6px 16px;
                border-radius: 20px;
                font-size: 13px;
                font-weight: 600;
                letter-spacing: 0.5px;
                text-transform: uppercase;
                display: inline-block;
                margin-bottom: 16px;
                border: 1px solid rgba(255,255,255,0.2);
            ">
                🤖 AGENTE IA CORPORATIVO 100% LOCAL · 0 TOKENS · CERO COSTOS
            </span>
            <h1 style="
                font-size: 2.8rem;
                font-weight: 700;
                background: linear-gradient(135deg, #ffffff 0%, #d1c4e9 50%, #b388ff 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 12px;
            ">
                Amershop Intelligent Assistant
            </h1>
            <p style="
                color: #b0b0c8;
                font-size: 1.15rem;
                max-width: 780px;
                margin: 0 auto 24px auto;
                line-height: 1.6;
            ">
                Atención corporativa automatizada para colaboradores y clientes. Impulsada por una arquitectura
                <strong>RAG Híbrida</strong> (FAISS + FastEmbed) y un modelo de lenguaje <strong>100% local en Ollama</strong>
                que garantiza privacidad total, cero consumo de tokens y respuestas precisas basadas en los documentos oficiales de la tienda.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # CTAS PRINCIPALES
    # -------------------------------------------------------------
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("💬 Abrir Chat del Asistente", use_container_width=True, type="primary"):
            st.session_state["current_page"] = "chat"
            st.rerun()

    with col2:
        if st.button("🔑 Iniciar Sesión / Registro", use_container_width=True):
            st.session_state["current_page"] = "login"
            st.rerun()

    with col3:
        if st.button("🚀 Acceso Rápido (Invitado)", use_container_width=True):
            st.session_state["authenticated"] = True
            st.session_state["username"] = None
            st.session_state["user_name"] = "Invitado"
            st.session_state["user_email"] = ""
            st.session_state["auth_type"] = "Acceso Invitado"
            st.session_state["messages"] = []
            st.session_state["current_page"] = "chat"
            st.rerun()

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # INDICADORES EN TIEMPO REAL
    # -------------------------------------------------------------
    status_color = "#00e676" if is_online else "#ff5252"
    status_text = "En Línea (Conectado)" if is_online else "Sin Conexión al Backend"

    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
    with mcol1:
        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(138,43,226,0.25); border-radius: 12px; padding: 16px; text-align: center;">
                <div style="font-size: 13px; color: #a0a0b8; text-transform: uppercase;">Estado Backend</div>
                <div style="font-size: 18px; font-weight: 600; color: {status_color}; margin-top: 4px;">● {status_text}</div>
            </div>
        """, unsafe_allow_html=True)

    with mcol2:
        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(138,43,226,0.25); border-radius: 12px; padding: 16px; text-align: center;">
                <div style="font-size: 13px; color: #a0a0b8; text-transform: uppercase;">Motor de IA</div>
                <div style="font-size: 18px; font-weight: 600; color: #b388ff; margin-top: 4px;">🦙 {model_name}</div>
            </div>
        """, unsafe_allow_html=True)

    with mcol3:
        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(138,43,226,0.25); border-radius: 12px; padding: 16px; text-align: center;">
                <div style="font-size: 13px; color: #a0a0b8; text-transform: uppercase;">Fragmentos Indexados</div>
                <div style="font-size: 18px; font-weight: 600; color: #ffffff; margin-top: 4px;">📚 {doc_count} Chunks (FAISS)</div>
            </div>
        """, unsafe_allow_html=True)

    with mcol4:
        st.markdown("""
            <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(138,43,226,0.25); border-radius: 12px; padding: 16px; text-align: center;">
                <div style="font-size: 13px; color: #a0a0b8; text-transform: uppercase;">Consumo de Tokens</div>
                <div style="font-size: 18px; font-weight: 600; color: #00e676; margin-top: 4px;">🪙 0 (100% Gratuito)</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # SECCIÓN: CARACTERÍSTICAS PRINCIPALES
    # -------------------------------------------------------------
    st.markdown("<h2 style='text-align: center; color: #ffffff; font-weight: 600;'>Funcionalidades de la Plataforma</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #a0a0b8; margin-bottom: 30px;'>Todo lo que necesitas para atención inteligente y gestión corporativa.</p>", unsafe_allow_html=True)

    fcol1, fcol2, fcol3 = st.columns(3)

    with fcol1:
        st.markdown("""
            <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(138,43,226,0.2); border-radius: 14px; padding: 22px; height: 100%;">
                <div style="font-size: 32px; margin-bottom: 12px;">🧠</div>
                <h3 style="color: #b388ff; font-size: 1.2rem; font-weight: 600;">Agente Local sin Tokens</h3>
                <p style="color: #c0c0d8; font-size: 0.95rem; line-height: 1.5;">
                    Utiliza modelos abiertos de última generación (Llama 3.2, Phi-3, Mistral) ejecutándose localmente con <strong>Ollama</strong>.
                    Sin suscripciones de tokens ni dependencia de APIs externas pagadas.
                </p>
            </div>
        """, unsafe_allow_html=True)

    with fcol2:
        st.markdown("""
            <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(138,43,226,0.2); border-radius: 14px; padding: 22px; height: 100%;">
                <div style="font-size: 32px; margin-bottom: 12px;">🔍</div>
                <h3 style="color: #b388ff; font-size: 1.2rem; font-weight: 600;">Búsqueda Híbrida Avanzada</h3>
                <p style="color: #c0c0d8; font-size: 0.95rem; line-height: 1.5;">
                    Combina búsqueda vectorial densa con <strong>FAISS</strong> y búsqueda léxica normalizada con expansión
                    de sinónimos en español (p. ej. "portátiles" ↔ "laptops") mediante <em>Reciprocal Rank Fusion</em>.
                </p>
            </div>
        """, unsafe_allow_html=True)

    with fcol3:
        st.markdown("""
            <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(138,43,226,0.2); border-radius: 14px; padding: 22px; height: 100%;">
                <div style="font-size: 32px; margin-bottom: 12px;">📁</div>
                <h3 style="color: #b388ff; font-size: 1.2rem; font-weight: 600;">Ingesta de 8 Formatos</h3>
                <p style="color: #c0c0d8; font-size: 0.95rem; line-height: 1.5;">
                    Soporta la lectura automatizada de <strong>PDF, DOCX, XLSX, PPTX, MD, CSV, JSON y HTML</strong>.
                    El catálogo Excel genera fichas estructuradas por producto.
                </p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    fcol4, fcol5, fcol6 = st.columns(3)

    with fcol4:
        st.markdown("""
            <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(138,43,226,0.2); border-radius: 14px; padding: 22px; height: 100%;">
                <div style="font-size: 32px; margin-bottom: 12px;">🔒</div>
                <h3 style="color: #b388ff; font-size: 1.2rem; font-weight: 600;">Seguridad & PostgreSQL</h3>
                <p style="color: #c0c0d8; font-size: 0.95rem; line-height: 1.5;">
                    Autenticación segura con hash <strong>bcrypt</strong>, usuarios corporativos precargados, registro
                    dinámico y persistencia del historial de conversaciones en PostgreSQL 16.
                </p>
            </div>
        """, unsafe_allow_html=True)

    with fcol5:
        st.markdown("""
            <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(138,43,226,0.2); border-radius: 14px; padding: 22px; height: 100%;">
                <div style="font-size: 32px; margin-bottom: 12px;">🔌</div>
                <h3 style="color: #b388ff; font-size: 1.2rem; font-weight: 600;">API REST Documentada</h3>
                <p style="color: #c0c0d8; font-size: 0.95rem; line-height: 1.5;">
                    Backend construido en <strong>FastAPI</strong> con OpenAPI / Swagger interactivo en <code>/docs</code>,
                    listo para conectar con aplicaciones móviles, WhatsApp bots o paneles web.
                </p>
            </div>
        """, unsafe_allow_html=True)

    with fcol6:
        st.markdown("""
            <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(138,43,226,0.2); border-radius: 14px; padding: 22px; height: 100%;">
                <div style="font-size: 32px; margin-bottom: 12px;">🐳</div>
                <h3 style="color: #b388ff; font-size: 1.2rem; font-weight: 600;">Docker & Lista para VPS</h3>
                <p style="color: #c0c0d8; font-size: 0.95rem; line-height: 1.5;">
                    Orquestación completa con <strong>Docker Compose</strong>. Redes aisladas, volúmenes persistentes,
                    healthchecks sincronizados y guía paso a paso para despliegue en cualquier VPS Linux.
                </p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # SECCIÓN: ARQUITECTURA INTEGRADA (DIAGRAMA)
    # -------------------------------------------------------------
    st.markdown("<h2 style='text-align: center; color: #ffffff; font-weight: 600;'>Arquitectura Integrada del Sistema</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #a0a0b8; margin-bottom: 25px;'>Flujo de datos entre los 4 contenedores orquestados con Docker Compose.</p>", unsafe_allow_html=True)

    st.markdown("""
        <div style="
            background: rgba(10, 8, 20, 0.85);
            border: 1px solid rgba(138, 43, 226, 0.3);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 35px;
        ">
            <div style="display: flex; flex-wrap: wrap; justify-content: space-around; align-items: center; gap: 15px;">
                <div style="background: rgba(138, 43, 226, 0.15); border: 1px solid rgba(138, 43, 226, 0.5); border-radius: 10px; padding: 15px 20px; text-align: center; min-width: 180px;">
                    <div style="font-size: 24px;">🌐</div>
                    <strong style="color: #ffffff;">Frontend</strong>
                    <div style="color: #b388ff; font-size: 12px;">Streamlit (Puerto 8501)</div>
                    <div style="color: #a0a0b8; font-size: 11px;">Landing + Chat + Auth</div>
                </div>
                <div style="font-size: 24px; color: #b388ff;">➔ HTTP ➔</div>
                <div style="background: rgba(0, 150, 136, 0.15); border: 1px solid rgba(0, 150, 136, 0.5); border-radius: 10px; padding: 15px 20px; text-align: center; min-width: 180px;">
                    <div style="font-size: 24px;">⚡</div>
                    <strong style="color: #ffffff;">Backend API</strong>
                    <div style="color: #80cbc4; font-size: 12px;">FastAPI (Puerto 8000)</div>
                    <div style="color: #a0a0b8; font-size: 11px;">RAG Agent + Endpoints</div>
                </div>
                <div style="font-size: 24px; color: #b388ff;">➔ Red Interna ➔</div>
                <div style="display: flex; flex-direction: column; gap: 10px;">
                    <div style="background: rgba(255, 112, 67, 0.15); border: 1px solid rgba(255, 112, 67, 0.5); border-radius: 8px; padding: 10px 16px; text-align: center;">
                        <span style="font-size: 16px;">🦙</span>
                        <strong style="color: #ffffff; font-size: 13px;"> Ollama Local</strong>
                        <span style="color: #ffab91; font-size: 11px;">(Puerto 11434 · Llama 3.2)</span>
                    </div>
                    <div style="background: rgba(65, 105, 225, 0.15); border: 1px solid rgba(65, 105, 225, 0.5); border-radius: 8px; padding: 10px 16px; text-align: center;">
                        <span style="font-size: 16px;">🐘</span>
                        <strong style="color: #ffffff; font-size: 13px;"> PostgreSQL 16</strong>
                        <span style="color: #90caf9; font-size: 11px;">(Usuarios e Historial)</span>
                    </div>
                    <div style="background: rgba(76, 175, 80, 0.15); border: 1px solid rgba(76, 175, 80, 0.5); border-radius: 8px; padding: 10px 16px; text-align: center;">
                        <span style="font-size: 16px;">🔎</span>
                        <strong style="color: #ffffff; font-size: 13px;"> FAISS Vector DB</strong>
                        <span style="color: #a5d6a7; font-size: 11px;">(Búsqueda Híbrida)</span>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # SECCIÓN: ENDPOINTS DE LA API
    # -------------------------------------------------------------
    st.markdown("<h2 style='text-align: center; color: #ffffff; font-weight: 600;'>Referencia Rápida de la API REST</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #a0a0b8; margin-bottom: 25px;'>Conecta cualquier cliente externo al backend de Amershop.</p>", unsafe_allow_html=True)

    api_tab1, api_tab2 = st.tabs(["Endpoints Principales", "Ejemplo de Consulta cURL"])

    with api_tab1:
        st.markdown("""
| Método | Endpoint | Descripción | Acceso |
| :---: | :--- | :--- | :---: |
| `GET` | `/` | Comprobación de estado general (*healthcheck*) | Público |
| `GET` | `/status` | Métricas y estado detallado del sistema (DB, fuentes, LLM) | Público |
| `POST` | `/chat` | Envía una consulta al Agente RAG (admite historial y usuario) | Público / Usuario |
| `POST` | `/login` | Valida credenciales de usuario registrado o corporativo | Público |
| `POST` | `/register` | Registra una nueva cuenta de usuario con hash seguro | Público |
| `GET` | `/history/{username}` | Recupera el historial de chat persistido en PostgreSQL | Autenticado |
| `GET` | `/docs` | Documentación interactiva Swagger UI / OpenAPI | Público |
        """)

    with api_tab2:
        st.code("""# Consultar al agente inteligente sin tokens
curl -X POST http://localhost:8000/chat \\
  -H "Content-Type: application/json" \\
  -d '{"prompt": "¿Cuál es la política de devoluciones y garantía en Amershop?"}'
        """, language="bash")

    st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # FOOTER
    # -------------------------------------------------------------
    st.markdown("""
        <hr style="border-color: rgba(138,43,226,0.2); margin-top: 40px; margin-bottom: 25px;">
        <div style="text-align: center; color: #8888a0; font-size: 13px;">
            Amershop — Plataforma Corporativa de IA · Proyecto de Desarrollo de Software II<br>
            Desarrollado con FastAPI, Streamlit, PostgreSQL, FAISS y Ollama (100% Local).
        </div>
    """, unsafe_allow_html=True)
