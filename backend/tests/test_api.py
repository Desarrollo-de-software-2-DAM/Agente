"""
Pruebas automatizadas de la API REST de FastAPI para Amershop.
Verifica endpoints de salud, registro, login, historial y chat.
"""

import pytest
from unittest.mock import MagicMock
import main as main_module
from db import User, Message, hash_password


def test_health_check_endpoint(client):
    """Verifica que el endpoint raíz responda con código 200 y status ok."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "Amershop" in data["message"]
    assert "llm_provider" in data


def test_system_status_endpoint(client, db_session):
    """Verifica el endpoint detallado /status para monitoreo y landing page."""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "store_name" in data
    assert data["store_name"] == "Amershop"
    assert "llm_provider" in data
    assert "total_users" in data


def test_register_success(client, db_session):
    """Prueba el registro exitoso de un nuevo usuario."""
    payload = {
        "username": "usuario_test",
        "email": "test@amershop.com",
        "password": "Password123!"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "Usuario registrado" in data["message"]

    # Verificar en la base de datos
    user = db_session.query(User).filter(User.username == "usuario_test").first()
    assert user is not None
    assert user.email == "test@amershop.com"


def test_register_duplicate_username(client, db_session):
    """Verifica que no se permita registrar usuarios duplicados."""
    user = User(username="duplicado", email="duplicado@amershop.com", password_hash=hash_password("123"))
    db_session.add(user)
    db_session.commit()

    payload = {
        "username": "duplicado",
        "email": "otro@amershop.com",
        "password": "123"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 400
    assert "ya existe" in response.json()["detail"]


def test_login_success(client, db_session):
    """Verifica el inicio de sesión con credenciales válidas."""
    user = User(username="logintest", email="login@amershop.com", password_hash=hash_password("clave_correcta"))
    db_session.add(user)
    db_session.commit()

    response = client.post("/login", json={"username": "logintest", "password": "clave_correcta"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "logintest"
    assert data["email"] == "login@amershop.com"


def test_login_invalid_password(client, db_session):
    """Verifica el rechazo con contraseña incorrecta."""
    user = User(username="logintest2", email="login2@amershop.com", password_hash=hash_password("clave_correcta"))
    db_session.add(user)
    db_session.commit()

    response = client.post("/login", json={"username": "logintest2", "password": "clave_erronea"})
    assert response.status_code == 401
    assert "incorrectos" in response.json()["detail"]


def test_history_empty_for_unknown_user(client):
    """Verifica que el historial devuelva lista vacía si el usuario no existe."""
    response = client.get("/history/usuario_inexistente")
    assert response.status_code == 200
    assert response.json() == {"messages": []}


def test_history_with_persisted_messages(client, db_session):
    """Verifica la recuperación de mensajes guardados en PostgreSQL/SQLite."""
    user = User(username="historial_user", email="hist@amershop.com", password_hash=hash_password("123"))
    db_session.add(user)
    db_session.commit()

    m1 = Message(user_id=user.id, role="user", content="¿Tienen envíos gratis?")
    m2 = Message(user_id=user.id, role="assistant", content="Sí, para compras mayores a $4.000.000 COP.")
    db_session.add_all([m1, m2])
    db_session.commit()

    response = client.get(f"/history/{user.username}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["messages"]) == 2
    assert data["messages"][0]["role"] == "user"
    assert data["messages"][1]["role"] == "assistant"


def test_chat_endpoint_with_mock_agent(client, db_session, monkeypatch):
    """Verifica el flujo del endpoint /chat asociando historial si el usuario está registrado."""
    user = User(username="chatuser", email="chatuser@amershop.com", password_hash=hash_password("123"))
    db_session.add(user)
    db_session.commit()

    # Mock del agente RAG
    mock_agent = MagicMock()
    mock_agent.query.return_value = {
        "answer": "La política de devoluciones es de 30 días.",
        "sources": ["politica_reembolso.docx"]
    }
    monkeypatch.setattr(main_module, "agent", mock_agent)

    payload = {
        "prompt": "¿Cuál es la política de devoluciones?",
        "chat_history": [],
        "username": "chatuser"
    }

    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "30 días" in data["answer"]
    assert "politica_reembolso.docx" in data["sources"]

    # Verificar que las interacciones se persistieron en la base de datos
    saved_messages = db_session.query(Message).filter(Message.user_id == user.id).all()
    assert len(saved_messages) == 2
    assert saved_messages[0].role == "user"
    assert saved_messages[1].role == "assistant"
