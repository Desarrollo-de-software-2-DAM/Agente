"""
Amershop — Frontend Streamlit
Integra Landing Page, Autenticación y Asistente IA Corporativo.
"""

import os
from pathlib import Path
import requests
import streamlit as st
from landing import render_landing_page, get_backend_status

# Configuración inicial de ventana
st.set_page_config(
    page_title="Amershop — Asistente IA Corporativo",
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
            json={
                "prompt": prompt,
                "chat_history": messages_history,
                "username": st.session_state.get("username"),
            },
            timeout=120,
        )
        if response.status_code == 200:
            return response.json().get("answer", "Sin respuesta.")
        else:
            return f"Error en el servidor: {response.status_code} - {response.text}"
    except requests.exceptions.ConnectionError:
        return "⚠️ No se pudo conectar con el servicio Backend. Verifica que el contenedor 'agente_backend' esté corriendo."
    except Exception as e:
        return f"Error de conexión: {e}"


def login_backend_api(username: str, password: str):
    """Valida usuario y contraseña contra el backend. Devuelve (ok, datos_o_mensaje_error)."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/login",
            json={"username": username, "password": password},
            timeout=15,
        )
        if response.status_code == 200:
            return True, response.json()
        return False, response.json().get("detail", "Usuario o contraseña incorrectos.")
    except requests.exceptions.ConnectionError:
        return False, "No se pudo conectar con el Backend. Verifica que el contenedor esté corriendo."
    except Exception as e:
        return False, f"Error de conexión: {e}"


def register_backend_api(username: str, email: str, password: str):
    """Crea un nuevo usuario en el backend. Devuelve (ok, datos_o_mensaje_error)."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/register",
            json={"username": username, "email": email, "password": password},
            timeout=15,
        )
        if response.status_code == 200:
            return True, response.json()
        return False, response.json().get("detail", "No se pudo completar el registro.")
    except requests.exceptions.ConnectionError:
        return False, "No se pudo conectar con el Backend. Verifica que el contenedor esté corriendo."
    except Exception as e:
        return False, f"Error de conexión: {e}"


def load_history_api(username: str) -> list:
    """Carga el historial de mensajes ya guardado de un usuario."""
    try:
        response = requests.get(f"{BACKEND_URL}/history/{username}", timeout=15)
        if response.status_code == 200:
            return response.json().get("messages", [])
    except Exception:
        pass
    return []


def inject_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
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
            background: rgba(12, 9, 25, 0.7) !important;
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
        </style>
    """, unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=280)
        st.markdown("<h1 style='text-align:center; color:#b388ff; font-size: 1.8rem; margin-bottom: 5px;'>Amershop</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#8888a0; font-size: 0.85rem; margin-bottom: 20px;'>Agente IA Corporativo</p>", unsafe_allow_html=True)

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

        st.markdown("### 🧭 Navegación")
        current = st.session_state.get("current_page", "landing")

        if st.button("🏠 Landing Page", use_container_width=True, type="secondary" if current != "landing" else "primary"):
            st.session_state["current_page"] = "landing"
            st.rerun()

        if st.button("💬 Chat del Asistente", use_container_width=True, type="secondary" if current != "chat" else "primary"):
            # Si no está autenticado, asignamos modo invitado suave
            if not st.session_state.get("authenticated", False):
                st.session_state["authenticated"] = True
                st.session_state["username"] = None
                st.session_state["user_name"] = "Invitado"
                st.session_state["user_email"] = ""
                st.session_state["auth_type"] = "Acceso Invitado"
            st.session_state["current_page"] = "chat"
            st.rerun()

        if not st.session_state.get("authenticated", False) or st.session_state.get("username") is None:
            if st.button("🔑 Iniciar Sesión / Registro", use_container_width=True, type="secondary" if current != "login" else "primary"):
                st.session_state["current_page"] = "login"
                st.rerun()

        st.markdown("---")
        st.markdown("### ⚡ Acciones Rápidas")
        if st.button("✨ Limpiar / Nuevo Chat", use_container_width=True):
            st.session_state["messages"] = []
            st.rerun()

        if st.session_state.get("authenticated", False) and st.session_state.get("username"):
            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                st.session_state["authenticated"] = False
                st.session_state["username"] = None
                st.session_state["user_name"] = None
                st.session_state["messages"] = []
                st.session_state["current_page"] = "landing"
                st.rerun()

        st.markdown("---")
        st.markdown("""
            <div style="font-size: 11px; color: #6e6e88; text-align: center;">
                Backend: <code>FastAPI</code><br>
                LLM: <code>Ollama Local (0 Tokens)</code><br>
                Vector Store: <code>FAISS</code><br>
                BD: <code>PostgreSQL 16</code>
            </div>
        """, unsafe_allow_html=True)


def render_login():
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

        tab_login, tab_registro = st.tabs(["Iniciar Sesión", "Registrarse"])

        with tab_login:
            with st.form("login_form"):
                username = st.text_input("Usuario", placeholder="admin, ventas, o tu usuario registrado")
                password = st.text_input("Contraseña", type="password", placeholder="••••••••", key="login_password")
                submitted = st.form_submit_button("Iniciar Sesión", use_container_width=True)

                if submitted:
                    if username and password:
                        ok, data = login_backend_api(username.strip().lower(), password)
                        if ok:
                            st.session_state["authenticated"] = True
                            st.session_state["username"] = data["username"]
                            st.session_state["user_name"] = data["username"].capitalize()
                            st.session_state["user_email"] = data.get("email", "")
                            st.session_state["auth_type"] = "Cuenta Registrada"
                            st.session_state["messages"] = load_history_api(data["username"])
                            st.session_state["current_page"] = "chat"
                            st.rerun()
                        else:
                            st.error(data)
                    else:
                        st.error("Por favor ingresa tu usuario y contraseña.")

        with tab_registro:
            with st.form("register_form"):
                new_username = st.text_input("Elige un usuario", placeholder="sin espacios, ej: jperez")
                new_email = st.text_input("Correo Electrónico", placeholder="tu@correo.com")
                new_password = st.text_input("Elige una contraseña", type="password", key="register_password")
                submitted_reg = st.form_submit_button("Crear Cuenta", use_container_width=True)

                if submitted_reg:
                    if new_username and new_email and new_password:
                        ok, data = register_backend_api(new_username.strip().lower(), new_email.strip(), new_password)
                        if ok:
                            st.success("Cuenta creada exitosamente. Ve a la pestaña 'Iniciar Sesión' para entrar.")
                        else:
                            st.error(data)
                    else:
                        st.error("Completa todos los campos para registrarte.")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if st.button("👤 Acceder como Invitado (Sin Guardar Historial)", use_container_width=True):
            st.session_state["authenticated"] = True
            st.session_state["username"] = None
            st.session_state["user_name"] = "Invitado"
            st.session_state["user_email"] = ""
            st.session_state["auth_type"] = "Acceso Invitado"
            st.session_state["messages"] = []
            st.session_state["current_page"] = "chat"
            st.rerun()

        if st.button("⬅️ Volver a la Landing Page", use_container_width=True):
            st.session_state["current_page"] = "landing"
            st.rerun()


def render_chat():
    st.header("🛒 Asistente Virtual Inteligente")
    st.write("Resuelve dudas sobre políticas, envíos, métodos de pago, garantías y catálogo de productos.")

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    suggestion_prompt = None
    if not st.session_state["messages"]:
        suggestions = [
            "¿Cuál es la política de devoluciones?",
            "¿Cuánto cuesta el envío express?",
            "¿En qué moneda están los precios?",
            "¿Tienen envío gratuito?",
            "¿Qué modelos de portátiles tienen?",
            "¿Cuál es el número de teléfono de la tienda?"
        ]
        cols = st.columns(3)
        for i, s in enumerate(suggestions):
            if cols[i % 3].button(s, key=f"sug_{i}", use_container_width=True):
                suggestion_prompt = s

    avatar_logo = LOGO_PATH if os.path.exists(LOGO_PATH) else "🤖"
    for msg in st.session_state["messages"]:
        av = avatar_logo if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=av):
            st.markdown(msg["content"])

    user_input = st.chat_input("Escribe tu pregunta sobre Amershop...")
    prompt = suggestion_prompt or user_input

    if prompt:
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=avatar_logo):
            with st.spinner("🧠 Consultando base de conocimiento con IA Local..."):
                answer = query_backend_api(prompt, st.session_state["messages"])
                st.markdown(answer)
                st.session_state["messages"].append({"role": "assistant", "content": answer})


def main():
    inject_custom_css()

    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "landing"

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    render_sidebar()

    # Router de navegación
    page = st.session_state.get("current_page", "landing")

    if page == "landing":
        render_landing_page()
    elif page == "login":
        render_login()
    elif page == "chat":
        render_chat()
    else:
        render_landing_page()


if __name__ == "__main__":
    main()
