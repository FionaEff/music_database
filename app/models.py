from typing import Optional
from enum import Enum
from app import db
import sqlalchemy as sa
import sqlalchemy.orm as so


# Formats for owned albums
class FormatEnum(Enum):
    vinyl = "vinyl"
    cd = "cd"
    digital = "digital"


album_genres = sa.Table(
    "album_genres",
    db.metadata,
    sa.Column("album_id", sa.ForeignKey("albums.id"), primary_key=True),
    sa.Column("genre_id", sa.ForeignKey("genres.id"), primary_key=True),
)


class Artists(db.Model):
    __tablename__ = "artists"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128), index=True, unique=True)
    country: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    year_of_founding: so.Mapped[Optional[int]] = so.mapped_column(
        sa.Integer, index=True
    )
    notes: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    albums: so.Mapped[list["Albums"]] = so.relationship(back_populates="artist")


class Genres(db.Model):
    __tablename__ = "genres"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(32), index=True, unique=True)

    albums: so.Mapped[list["Albums"]] = so.relationship(
        secondary=album_genres, back_populates="genres"
    )


class Albums(db.Model):
    __tablename__ = "albums"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    artist_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Artists.id), index=True)
    discogs_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer, unique=True)

    title: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    year: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)
    format: so.Mapped[FormatEnum] = so.mapped_column(
        sa.Enum(FormatEnum, name="format_enum")
    )
    label: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    cover_path: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    notes: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    artist: so.Mapped["Artists"] = so.relationship(back_populates="albums")

    tracks: so.Mapped[list["Tracks"]] = so.relationship(
        back_populates="album", cascade="all, delete-orphan"
    )

    genres: so.Mapped[list["Genres"]] = so.relationship(
        secondary=album_genres, back_populates="albums"
    )


class Tracks(db.Model):
    __tablename__ = "tracks"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    album_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Albums.id), index=True)

    title: so.Mapped[str] = so.mapped_column(sa.String(128), index=True)
    track_number: so.Mapped[int] = so.mapped_column(sa.Integer, index=True)
    duration_seconds: so.Mapped[int] = so.mapped_column(sa.Integer)

    album: so.Mapped["Albums"] = so.relationship(back_populates="tracks")
