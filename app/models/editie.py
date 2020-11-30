from __future__ import annotations

import enum
from sqlalchemy.sql import Select, expression

from app.misc import db
from app.models.base import BaseModel, TimedBaseModel
from app.models.locatie import StraatRelatedModel

#############################################
# Editie
#############################################
class Editie(TimedBaseModel):
    __tablename__ = "edities"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, index=True, unique=True)
    naam = db.Column(db.String)
    url = db.Column(db.String)
    cover = db.Column(db.String)

    query: Select


class EditieRelatedModel(BaseModel):
    __abstract__ = True

    editie_id = db.Column(
        db.ForeignKey(f"{Editie.__tablename__}.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )


#############################################
# Bezorging
#############################################
class BezorgingsStatus(enum.Enum):
    open = 1
    bezig = 2
    gedaan = 3

class Bezorging(TimedBaseModel, EditieRelatedModel, StraatRelatedModel):
    __tablename__ = "bezorging"

    id = db.Column(db.BigInteger, autoincrement=True, primary_key=True, index=True, unique=True)
    status = db.Column(db.Enum(BezorgingsStatus), server_default=BezorgingsStatus.open.name, nullable=False)
    opmerking = db.Column(db.Text)

    query: Select

class BezorgingRelatedModel(BaseModel):
    __abstract__ = True

    groep_id = db.Column(
        db.ForeignKey(f"{Bezorging.__tablename__}.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
