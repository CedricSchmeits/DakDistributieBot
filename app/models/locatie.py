from __future__ import annotations

import enum
from sqlalchemy.sql import Select, expression

from app.misc import db
from app.models.base import BaseModel
from app.models.groep import GroepRelatedModel

class LocatieModel(GroepRelatedModel):
    __abstract__ = True

    name = db.Column(db.String)
    opmerking = db.Column(db.Text)


#############################################
# Plaats
#############################################
class Plaats(LocatieModel):
    __tablename__ = "plaatsen"

    id = db.Column(db.BigInteger, autoincrement=True, primary_key=True, index=True, unique=True)

    query: Select


class PlaatsRelatedModel(BaseModel):
    __abstract__ = True

    plaats_id = db.Column(
        db.ForeignKey(f"{Plaats.__tablename__}.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )

#############################################
# Wijk
#############################################
class Wijk(LocatieModel, PlaatsRelatedModel):
    __tablename__ = "wijken"

    id = db.Column(db.BigInteger, autoincrement=True, primary_key=True, index=True, unique=True)

    query: Select


class WijkRelatedModel(BaseModel):
    __abstract__ = True

    straat_id = db.Column(
        db.ForeignKey(f"{Wijk.__tablename__}.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )


#############################################
# Straat
#############################################
class Straat(LocatieModel, PlaatsRelatedModel, WijkRelatedModel):
    __tablename__ = "straten"

    id = db.Column(db.BigInteger, autoincrement=True, primary_key=True, index=True, unique=True)

    query: Select


class StraatRelatedModel(BaseModel):
    __abstract__ = True

    straat_id = db.Column(
        db.ForeignKey(f"{Straat.__tablename__}.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )


#############################################
# Huis
#############################################
class Gewenst(enum.Enum):
    ja = 1
    nee = 2

class Huis(StraatRelatedModel):
    __tablename__ = "huizen"

    id = db.Column(db.BigInteger, autoincrement=True, primary_key=True, index=True, unique=True)
    nummer = db.Column(db.String, nullable=False)
    gewenst = db.Column(db.Enum(Gewenst), server_default=Gewenst.nee.name, nullable=False)

    query: Select


class HuisRelatedModel(BaseModel):
    __abstract__ = True

    straat_id = db.Column(
        db.ForeignKey(f"{Huis.__tablename__}.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
