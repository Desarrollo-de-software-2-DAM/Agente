"""
Acceso a la base de datos PostgreSQL: usuarios y su historial de chat.
"""
import os
import logging
from datetime import datetime, timezone

import bcrypt
from sqlalchemy import create_engine, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker, Session

from config import AUTH_USERS

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "")


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    messages: Mapped[list["Message"]] = relationship(back_populates="user")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    role: Mapped[str] = mapped_column(String(16))  # "user" | "assistant"
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="messages")


engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db():
    """Abre una sesión de base de datos y la cierra sola al terminar (para FastAPI Depends)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    """Convierte una contraseña en texto plano en un hash seguro para guardar."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Compara una contraseña escrita por el usuario contra el hash guardado."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def seed_corporate_users(db: Session):
    """Migra los usuarios corporativos de config.py a la base de datos, solo si no existen aún."""
    for username, plain_password in AUTH_USERS.items():
        exists = db.query(User).filter(User.username == username).first()
        if not exists:
            db.add(User(
                username=username,
                email=f"{username}@amershop.com",
                password_hash=hash_password(plain_password),
            ))
            logger.info(f"Usuario corporativo migrado a la base de datos: {username}")
    db.commit()