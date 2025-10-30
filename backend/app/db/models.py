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
    name = sa.Column(sa.String(255), nullable=True)  # ✅ Added: display name
    email = sa.Column(sa.String(255), unique=True, nullable=False, index=True)
    hashed_password = sa.Column(sa.String(255), nullable=False)
    is_active = sa.Column(sa.Boolean(), default=True)
    is_superuser = sa.Column(sa.Boolean(), default=False)
    created_at = sa.Column(sa.DateTime(), default=datetime.utcnow)
    updated_at = sa.Column(sa.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    avatar_url = sa.Column(sa.String(512), nullable=True)
    preferences = sa.Column(sa.JSON, default=lambda: {
        "theme": "light",
        "language": "en",
        "notifications": True
    })

    # ✅ Relationships
    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")
    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    comparisons = relationship("Comparison", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User id={self.id} email={self.email} active={self.is_active}>"


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

    # ✅ Add this line
    summaries = relationship("Summary", back_populates="document", cascade="all, delete-orphan")


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    document_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    name = sa.Column(sa.String(255), default="Conversation")
    meta_data = sa.Column(sa.JSON, default={})
    created_at = sa.Column(sa.DateTime(), default=datetime.utcnow)

    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    document = relationship("Document")


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


class Summary(Base):
    __tablename__ = "summaries"

    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    document_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)

    style = sa.Column(sa.String(64), default="executive")
    length = sa.Column(sa.String(32), default="medium")
    content = sa.Column(sa.Text, nullable=False)
    key_points = sa.Column(sa.JSON, default=list)
    word_count = sa.Column(sa.Integer)
    confidence = sa.Column(sa.Float)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    meta_data = sa.Column(sa.JSON, default=dict)

    document = relationship("Document", back_populates="summaries")


class Comparison(Base):
    __tablename__ = "comparisons"

    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    document_id1 = sa.Column(UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"))
    document_id2 = sa.Column(UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"))
    comparison_type = sa.Column(sa.String(50))
    status = sa.Column(sa.String(50), default="processing")
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    completed_at = sa.Column(sa.DateTime, nullable=True)
    summary = sa.Column(sa.JSON, default=dict)
    changes = sa.Column(sa.JSON, default=dict)
    category_breakdown = sa.Column(sa.JSON, default=dict)
    diff_url = sa.Column(sa.String(512))
    side_by_side_url = sa.Column(sa.String(512))
    meta_data = sa.Column(sa.JSON, default=dict) 

    # ✅ Relationships
    user = relationship("User", back_populates="comparisons")
    document1 = relationship("Document", foreign_keys=[document_id1])
    document2 = relationship("Document", foreign_keys=[document_id2])

    def to_dict(self, includeDetails: bool = True):
        base = {
            "id": str(self.id),
            "documentId1": str(self.document_id1) if self.document_id1 else None,
            "documentId2": str(self.document_id2) if self.document_id2 else None,
            "comparisonType": self.comparison_type,
            "status": self.status,
            "createdAt": self.created_at.isoformat(),
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
            "summary": self.summary or {},
            "categoryBreakdown": self.category_breakdown or {},
            "diffUrl": self.diff_url,
            "sideBySideUrl": self.side_by_side_url,
        }
        if includeDetails:
            base["changes"] = self.changes or {}
        return base

    def to_summary(self):
        return {
            "id": str(self.id),
            "document1Name": self.summary.get("document1Name") if self.summary else None,
            "document2Name": self.summary.get("document2Name") if self.summary else None,
            "status": self.status,
            "createdAt": self.created_at.isoformat(),
            "summary": {
                "totalChanges": (self.summary or {}).get("totalChanges"),
                "similarityScore": (self.summary or {}).get("similarityScore"),
            },
        }
    
