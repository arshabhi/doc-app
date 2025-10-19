# app/db/models.py
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from app.db.session import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = sa.Column(sa.String(255), unique=True, nullable=False, index=True)
    hashed_password = sa.Column(sa.String(255), nullable=False)
    is_active = sa.Column(sa.Boolean(), default=True)
    is_superuser = sa.Column(sa.Boolean(), default=False)
    created_at = sa.Column(sa.DateTime(), default=datetime.utcnow)

    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")
    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    owner_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = sa.Column(sa.String(512))
    content_type = sa.Column(sa.String(128))
    uploaded_at = sa.Column(sa.DateTime(), default=datetime.utcnow)
    meta_data = sa.Column(sa.JSON, default={})

    owner = relationship("User", back_populates="documents")
    embeddings = relationship("Embedding", back_populates="document", cascade="all, delete-orphan")


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = sa.Column(sa.String(255), default="Conversation")
    created_at = sa.Column(sa.DateTime(), default=datetime.utcnow)

    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    session_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role = sa.Column(sa.Enum("user", "assistant", "system", name="role_enum"), nullable=False)
    content = sa.Column(sa.Text, nullable=False)
    created_at = sa.Column(sa.DateTime(), default=datetime.utcnow)
    meta_data = sa.Column(sa.JSON, default={})

    session = relationship("ChatSession", back_populates="messages")


class Embedding(Base):
    __tablename__ = "embeddings"
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    document_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_id = sa.Column(sa.String(128), nullable=False)  # e.g. "docid_0"
    vector_id = sa.Column(sa.Integer, nullable=True, index=True)  # id in FAISS/Vector DB
    text = sa.Column(sa.Text, nullable=False)
    created_at = sa.Column(sa.DateTime(), default=datetime.utcnow)

    document = relationship("Document", back_populates="embeddings")
