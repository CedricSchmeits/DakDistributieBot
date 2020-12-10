from __future__ import annotations

from sqlalchemy.sql import Select, expression

from app.misc import db
from app.models.base import BaseModel


class Groep(BaseModel):
    __tablename__ = "groepen"

    id = db.Column(db.BigInteger, autoincrement=True, primary_key=True, index=True, unique=True)
    chatId = db.Column(db.BigInteger, unique=True)

    query: Select


class GroepRelatedModel(BaseModel):
    __abstract__ = True

    groep_id = db.Column(
        db.ForeignKey(f"{Groep.__tablename__}.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
