from typing import Optional
from app import db
import sqlalchemy as sa
import sqlalchemy.orm as so


class Artists(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128), index=True, unique=True)
    country: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    year_of_founding: so.Mapped[str] = so.mapped_column(sa.String(4), index=True)
    notes: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))


class Genres(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(32), index=True)


class Albums(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    artist_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Artists.id), index=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    year: so.Mapped[str] = so.mapped_column(sa.String(4))
    genre: so.Mapped[str] = so.mapped_column(sa.ForeignKey(Genres.id), index=True)
    format: so.Mapped[str] = so.mapped_column(sa.String(10))
    label: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    cover_path: so.Mapped[str] = so.mapped_column(sa.String(128))
    notes: so.Mapped[str] = so.mapped_column(sa.String(256))


class Tracks(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    albums_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Albums.id), index=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(128), index=True)
    track_number: so.Mapped[str] = so.mapped_column(sa.String(2))
    duration: so.Mapped[str] = so.mapped_column(sa.String(5))
