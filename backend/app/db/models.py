from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship as orm_relationship

from app.db.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    document_id = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    filename = Column(
        String,
        nullable=False,
    )

    file_hash = Column(
        String,
        nullable=True,
        index=True,
    )

    uploaded_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    pages = orm_relationship(
        "Page",
        back_populates="document",
        cascade="all, delete-orphan",
    )


class Page(Base):
    __tablename__ = "pages"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    document_id = Column(
        Integer,
        ForeignKey("documents.id"),
        nullable=False,
    )

    page_number = Column(
        Integer,
        nullable=False,
    )

    printed_page = Column(
        String,
        nullable=True,
    )

    text = Column(
        Text,
        nullable=False,
    )

    document = orm_relationship(
        "Document",
        back_populates="pages",
    )

    facts = orm_relationship(
        "Fact",
        back_populates="page",
        cascade="all, delete-orphan",
    )


class Fact(Base):
    __tablename__ = "facts"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    subject = Column(
        String,
        nullable=False,
    )

    predicate = Column(
        String,
        nullable=False,
    )

    value = Column(
        String,
        nullable=False,
    )

    value_type = Column(
        String,
        nullable=False,
    )

    unit = Column(
        String,
        nullable=True,
    )

    period = Column(
        String,
        nullable=True,
    )

    scope = Column(
        Text,
        nullable=True,
    )

    confidence = Column(
        Float,
        nullable=False,
    )

    extraction_method = Column(
        String,
        nullable=False,
        default="llm",
    )

    evidence_text = Column(
        Text,
        nullable=False,
    )

    evidence_verified = Column(
        Integer,
        nullable=False,
        default=0,
    )

    page_id = Column(
        Integer,
        ForeignKey("pages.id"),
        nullable=False,
    )

    page = orm_relationship(
        "Page",
        back_populates="facts",
    )

    relationship_memberships = orm_relationship(
        "RelationshipFact",
        back_populates="fact",
        cascade="all, delete-orphan",
    )


class FactRelationship(Base):
    """
    Represents a logical relationship between
    one or more facts.

    Examples:

    CORROBORATES:
        Fact A <-> Fact B

    RECONCILED:
        Fact A + Fact B = Fact C

    LIKELY_DISAGREEMENT:
        Fact A <-> Fact B
    """

    __tablename__ = "fact_relationships"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    relationship_type = Column(
        String,
        nullable=False,
    )

    confidence = Column(
        Float,
        nullable=False,
    )

    explanation = Column(
        Text,
        nullable=False,
    )

    facts = orm_relationship(
        "RelationshipFact",
        back_populates="relationship",
        cascade="all, delete-orphan",
    )


class RelationshipFact(Base):
    """
    Associates a fact with a relationship.

    role examples:

        source
        compared
        component
        total
        supporting
    """

    __tablename__ = "relationship_facts"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    relationship_id = Column(
        Integer,
        ForeignKey("fact_relationships.id"),
        nullable=False,
    )

    fact_id = Column(
        Integer,
        ForeignKey("facts.id"),
        nullable=False,
    )

    role = Column(
        String,
        nullable=False,
        default="supporting",
    )

    relationship = orm_relationship(
        "FactRelationship",
        back_populates="facts",
    )

    fact = orm_relationship(
        "Fact",
        back_populates="relationship_memberships",
    )