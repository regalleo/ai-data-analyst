"""
SQLAlchemy models for the AI Data Analyst application.
Implements multi-tenant data isolation with proper relationships.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

# Import Base from database.py to avoid circular imports
from database import Base


class User(Base):
    """
    User model with email as unique identifier.
    All datasets are owned by a user, enabling multi-tenant isolation.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # ✅ FIXED
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationship to datasets - enables cascade delete
    datasets = relationship(
        "Dataset",
        back_populates="owner",
        cascade="all, delete-orphan"
    )


class Dataset(Base):
    """
    Dataset model storing metadata and schema for uploaded CSV files.
    Each dataset belongs to exactly one user (multi-tenant isolation).
    """
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    table_name = Column(String(255), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    schema_info = Column(Text, nullable=True)
    description = Column(Text, nullable=True)

    # ✅ FIXED
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    owner = relationship("User", back_populates="datasets")

    rag_documents = relationship(
        "DatasetSchemaDoc",
        back_populates="dataset",
        cascade="all, delete-orphan"
    )


class DatasetSchemaDoc(Base):
    """
    Stores pre-processed documentation for each dataset column.
    Used by RAG to provide context-aware answers about datasets.
    """
    __tablename__ = "dataset_schema_docs"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(
        Integer,
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False
    )

    content = Column(Text, nullable=False)
    column_name = Column(String(255), nullable=True)

    # ✅ FIXED
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    dataset = relationship("Dataset", back_populates="rag_documents")
