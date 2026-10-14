"""
Amershop — Frontend Streamlit
"""

import os
from pathlib import Path
import requests
import streamlit as st
import streamlit.components.v1 as components

# Configuración inicial de ventana
st.set_page_config(
    page_title="Amershop — Asistente IA",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# URL del backend (obtenida desde la variable de entorno de Docker)
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")

_project_root = Path(__file__).resolve().parent
LOGO_PATH = os.path.join(_project_root, "assets", "logo.jpg")


def query_backend_api(prompt: str, messages_history: list) -> str:
    """Envía la consulta al contenedor del Backend por HTTP."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={"prompt": prompt, "chat_history": messages_history},
            timeout=60,
        )
        if response.status_code == 200:
            return response.json().get("answer", "Sin respuesta.")
        else:
            return f"Error en el servidor: {response.status_code} - {response.text}"
    except requests.exceptions.ConnectionError:
        return "⚠️ No se pudo conectar con el servicio Backend. Verifica que el contenedor esté corriendo."
    except Exception as e:
        return f"Error de conexión: {e}"


def inject_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&display=swap');
        .stMarkdown, p, h1, h2, h3, h4, h5, h6, li, label, div[data-testid="stMarkdownContainer"] {
            font-family: 'Outfit', sans-serif !important;
        }
        [data-testid="stAppViewContainer"] {
            background: radial-gradient(circle at 10% 20%, #0d081c 0%, #06040b 50%, #000000 100%);
            color: #f0f0f5;
        }
        [data-testid="stHeader"] {
            background: rgba(12, 9, 25, 0.75) !important;
            backdrop-filter: blur(12px) !important;
            border-bottom: 1px solid rgba(138, 43, 226, 0.2) !important;
        }
        [data-testid="stSidebar"] {
            background: rgba(12, 9, 25, 0.5) !important;
            backdrop-filter: blur(16px);
            border-right: 1px solid rgba(138, 43, 226, 0.15);
        }
        .stButton>button {
            background: linear-gradient(145deg, #1a1a2e, #12121e);
            color: #d1d1e0;
            border: 1px solid rgba(138, 43, 226, 0.3);
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background: linear-gradient(145deg, #252542, #181829);
            border-color: rgba(138, 43, 226, 0.6);
            color: white;
            transform: translateY(-2px);
        }
        [data-testid="stChatMessage"] {
            background: linear-gradient(145deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 24px;
            border: 1px solid rgba(138, 43, 226, 0.1);
        }
        [data-testid="stChatInput"] > div, div[data-baseweb="input"] {
            border: 1px solid rgba(138, 43, 226, 0.6) !important;
            border-radius: 12px !important;
            background: rgba(15, 12, 28, 0.85) !important;
            color: white !important;
        }
        .user-profile-badge {
            background: rgba(138, 43, 226, 0.15);
            border: 1px solid rgba(138, 43, 226, 0.3);
            border-radius: 12px;
            padding: 14px;
            text-align: center;
            margin-bottom: 20px;
        }
        @keyframes pulse-green {
            0% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.8); transform: scale(0.95); }
            70% { box-shadow: 0 0 0 12px rgba(0, 255, 136, 0); transform: scale(1.05); }
            100% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0); transform: scale(0.95); }
        }
        .led-banner {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 14px;
            background: rgba(12, 8, 25, 0.85);
            border: 1px solid rgba(138, 43, 226, 0.6);
            border-radius: 20px;
            padding: 14px 22px;
            margin: 15px 0 25px 0;
            box-shadow: 0 0 25px rgba(138, 43, 226, 0.35), inset 0 0 15px rgba(138, 43, 226, 0.2);
            backdrop-filter: blur(12px);
        }
        .led-dot {
            width: 12px; height: 12px; background-color: #00ff88;
            border-radius: 50%; display: inline-block;
            animation: pulse-green 1.8s infinite;
            box-shadow: 0 0 10px #00ff88, 0 0 20px #00ff88;
        }
        .led-text {
            color: #ffffff; font-weight: 700; font-size: 15px; letter-spacing: 1.8px; text-transform: uppercase;
        }
        .led-subtext { color: #b0b0e0; font-size: 13px; font-weight: 400; }
        </style>
    """, unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=280)
        st.markdown("<h1 style='text-align:center; color:#b388ff;'>Amershop</h1>", unsafe_allow_html=True)

        if st.session_state.get("authenticated", False):
            user_name = st.session_state.get("user_name", "Usuario")
            user_email = st.session_state.get("user_email", "")
            auth_type = st.session_state.get("auth_type", "Invitado")

            st.markdown(f"""
                <div class="user-profile-badge">
                    <div style="font-size: 24px;">👤</div>
                    <div style="font-weight: 600; color: #ffffff;">{user_name}</div>
                    <div style="font-size: 12px; color: #b388ff;">{user_email if user_email else auth_type}</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("### Acciones Rápidas")
        if st.button("✨ Nuevo Chat", use_container_width=True):
            st.session_state["messages"] = []
            st.rerun()

        if st.session_state.get("authenticated", False):
            st.markdown("---")
            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                st.session_state["authenticated"] = False
                st.session_state["messages"] = []
                st.rerun()


def render_login():
    inject_custom_css()
    col1, col2, col3 = st.columns([1, 2.2, 1])
    with col2:
        img_col1, img_col2, img_col3 = st.columns([1, 1.2, 1])
        with img_col2:
            if os.path.exists(LOGO_PATH):
                st.image(LOGO_PATH, width=140)

        st.markdown("""
            <div style="text-align: center; margin-bottom: 15px;">
                <h1 style="color: #b388ff; font-weight: 600;">Bienvenido a Amershop</h1>
                <p style="color: #a0a0c0; font-size: 14px;">Inicia sesión para acceder al asistente virtual corporativo</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            email = st.text_input("Correo Electrónico", placeholder="usuario@amershop.com")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Iniciar Sesión con Correo", use_container_width=True)

            if submitted:
                if email and password:
                    st.session_state["authenticated"] = True
                    st.session_state["user_name"] = email.split("@")[0].capitalize()
                    st.session_state["user_email"] = email
                    st.session_state["auth_type"] = "Cuenta Corporativa"
                    st.rerun()
                else:
                    st.error("Por favor ingresa tu correo y contraseña.")

        if st.button("👤 Acceder como Invitado", use_container_width=True):
            st.session_state["authenticated"] = True
            st.session_state["user_name"] = "Invitado"
            st.session_state["user_email"] = ""
            st.session_state["auth_type"] = "Acceso Invitado"
            st.rerun()


def main():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        render_login()
        return

    inject_custom_css()
    render_sidebar()

    st.header("¿En qué podemos ayudarte hoy?")
    st.write("Resuelve tus dudas sobre productos, envíos, devoluciones y más.")

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    suggestion_prompt = None
    if not st.session_state["messages"]:
        st.markdown("""
            <div class="led-banner">
                <span class="led-dot"></span>
                <span class="led-text">ACTIVO LAS 24 HORAS</span>
                <span class="led-subtext">• ATENCIÓN Y SOPORTE CONTINUO 24/7</span>
            </div>
        """, unsafe_allow_html=True)

        suggestions = [
            "¿Cuál es la política de devoluciones?",
            "¿Cuánto cuesta el envío express?",
            "¿En qué moneda están los precios?",
            "¿Tienen envío gratuito?",
        ]
        cols = st.columns(2)
        for i, s in enumerate(suggestions):
            if cols[i % 2].button(s, key=f"sug_{i}"):
                suggestion_prompt = s

    avatar_logo = LOGO_PATH if os.path.exists(LOGO_PATH) else "🐉"
    for msg in st.session_state["messages"]:
        av = avatar_logo if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=av):
            st.markdown(msg["content"])

    user_input = st.chat_input("Escribe tu pregunta...")
    prompt = suggestion_prompt or user_input

    if prompt:
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=avatar_logo):
            with st.spinner("✨ Preparando tu respuesta..."):
                answer = query_backend_api(prompt, st.session_state["messages"])
                st.markdown(answer)
                st.session_state["messages"].append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()