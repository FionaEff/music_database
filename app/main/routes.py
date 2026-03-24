import sqlalchemy as sa
from sqlalchemy import or_
from sqlalchemy.orm import selectinload
from flask import render_template, flash, redirect, url_for, request
from app import db, Config
from app.main import bp
from app.main.forms import AddAlbumForm, EditArtistForm
from app.models import (
    Artists,
    Albums,
    Tracks,
    Genres,
)


@bp.route("/", methods=["GET"])
@bp.route("/index", methods=["GET"])
def index():
    albums = db.session.query(Albums).order_by(Albums.id.desc()).limit(5)
    return render_template("index.html", title="Home", albums=albums)


@bp.route("/albums", methods=["GET"])
def albums():
    albums = (
        db.session.query(Albums)
        .options(selectinload(Albums.artist))
        .join(Artists)
        .order_by(Artists.name, Albums.year)
        .all()
    )
    return render_template(
        "albums.html",
        title="Albums",
        albums=albums,
    )


@bp.route("/album_details/<int:album_id>", methods=["GET"])
def album_details(album_id):

    album = (
        db.session.query(Albums)
        .options(
            selectinload(Albums.artist),
            selectinload(Albums.genres),
            selectinload(Albums.tracks),
        )
        .filter_by(id=album_id)
        .first()
    )

    if not album:
        flash("Album not found.")
        return redirect(url_for("main.albums"))

    tracks = sorted(album.tracks, key=lambda t: t.track_number or 0)

    return render_template(
        "album_details.html", title=album.title, album=album, tracks=tracks
    )


@bp.route("/add_album", methods=["GET", "POST"])
def add_album():
    form = AddAlbumForm()

    genres = Genres.query.order_by(Genres.name).all()
    artists = Artists.query.order_by(Artists.name).all()

    form.existing_genre.choices = [(0, "---")] + [
        (g.id, g.name) for g in genres
    ]  # Filling genre dropdown menu, starting with ---
    form.existing_artist.choices = [(0, "---")] + [
        (g.id, g.name) for g in artists
    ]  # Filling artists dropdown menu, starting with ---

    if form.validate_on_submit():

        # Artist handling
        if form.new_artist.data:
            artist = Artists(name=form.new_artist.data)
            db.session.add(artist)
            db.session.flush()
        else:
            artist = db.session.get(Artists, form.existing_artist.data)

        # Genre handling
        if form.new_genre.data:
            genre = Genres(name=form.new_genre.data)
            db.session.add(genre)
            db.session.flush()
        else:
            genre = db.session.get(Genres, form.existing_genre.data)

        # Add album to database
        new_album = Albums(
            title=form.album_name.data,
            artist=artist,
            year=form.year.data,
            label=form.label.data,
            format=form.format.data,
            notes=form.notes.data,
            discogs_id=form.discogs_id.data,
        )

        # Add more than one genre to album
        if genre:
            new_album.genres.append(genre)

        db.session.add(new_album)
        db.session.commit()

        if form.discogs_id.data:
            from app.services.discogs import (
                fetch_discogs_data,
                extract_tracks,
                import_tracks,
                download_discogs_cover,
            )

            data = fetch_discogs_data(form.discogs_id.data)

            if data:
                # Import tracks
                tracks = extract_tracks(data)
                import_tracks(new_album, tracks, db)

                # Download cover
                cover_path = download_discogs_cover(form.discogs_id.data, new_album.id)

                if cover_path:
                    new_album.cover_path = cover_path

        flash("The album has been added to de database.")
        return redirect(url_for("main.edit_tracks", album_id=new_album.id))

    return render_template("add_album.html", title="Add Album", form=form)


@bp.route("/album/<int:album_id>/tracks", methods=["GET", "POST"])
def edit_tracks(album_id):

    album = db.session.get(Albums, album_id)

    if not album:
        flash("Album not found.")
        return redirect(url_for("main.albums"))

    if request.method == "POST":

        # Delete a track
        delete_id = request.form.get("delete_track_id")
        if delete_id:
            track = db.session.get(Tracks, int(delete_id))
            if track:
                db.session.delete(track)
                db.session.commit()
                flash("Track deleted.")
            return redirect(url_for("main.edit_tracks", album_id=album.id))

        # Update existing track
        for track in album.tracks:
            track.title = request.form.get(f"title_{track.id}")

            try:
                track.track_number = int(request.form.get(f"number_{track.id}") or 0)
                track.duration_seconds = int(
                    request.form.get(f"duration_{track.id}") or 0
                )
            except ValueError:
                pass

        # Add new track
        new_title = request.form.get("new_title")
        new_track_number = request.form.get("new_track_number")
        new_duration = request.form.get("new_duration")

        if new_title and new_title.strip():
            new_track = Tracks(
                album=album,
                title=new_title.strip(),
                track_number=int(new_track_number or 0),
                duration_seconds=int(new_duration or 0),
            )
            db.session.add(new_track)

        db.session.commit()
        flash("Tracks updated.")

        return redirect(url_for("main.edit_tracks", album_id=album.id))

    tracks = sorted(album.tracks, key=lambda t: t.track_number)

    return render_template(
        "edit_tracks.html", title=album.title, album=album, tracks=tracks
    )


@bp.route("/artists", methods=["GET"])
def artists():

    artists = db.session.query(Artists).order_by(Artists.name).all()

    return render_template("artists.html", title="Artists", artists=artists)


@bp.route("/artist_details/<int:artist_id>", methods=["GET"])
def artist_details(artist_id):

    artist = (
        db.session.query(Artists)
        .options(selectinload(Artists.albums))
        .filter_by(id=artist_id)
        .first()
    )

    if not artist:
        flash("Artist not found.")
        return redirect(url_for("main.artists"))

    albums = sorted(artist.albums, key=lambda a: a.year or 0)

    return render_template(
        "artist_details.html", title=artist.name, artist=artist, albums=albums
    )


@bp.route("/artist/<int:artist_id>/edit", methods=["GET", "POST"])
def edit_artist(artist_id):

    artist = db.session.get(Artists, artist_id)

    if not artist:
        flash("Artist not found.")
        return redirect(url_for("main.artists"))

    form = EditArtistForm(obj=artist)

    if form.validate_on_submit():
        artist.name = form.name.data
        artist.country = form.country.data
        artist.year_of_founding = form.year_of_founding.data
        artist.notes = form.notes.data

        db.session.commit()

        flash("Artist updated.")
        return redirect(url_for("main.artist_details", artist_id=artist.id))

    return render_template(
        "edit_artist.html", title=f"Edit {artist.name}", form=form, artist=artist
    )


@bp.route("/artist/add", methods=["GET", "POST"])
def add_artist():

    form = EditArtistForm()

    if form.validate_on_submit():

        # Avoid duplicates
        existing = db.session.query(Artists).filter_by(name=form.name.data).first()
        if existing:
            flash("Artist already exists.")
            return redirect(url_for("main.artist_details", artist_id=existing.id))

        artist = Artists(
            name=form.name.data,
            country=form.country.data,
            year_of_founding=form.year_of_founding.data or 0,
            notes=form.notes.data,
        )

        db.session.add(artist)
        db.session.commit()

        flash("Artist added.")
        return redirect(url_for("main.artist_details", artist_id=artist.id))

    return render_template("edit_artist.html", title="Add a new Artist", form=form)


@bp.route("/artist/<int:artist_id>/delete", methods=["POST"])
def delete_artist(artist_id):

    artist = db.session.get(Artists, artist_id)

    if not artist:
        flash("Artist not found.")
        return redirect(url_for("main.artists"))

    # Check if artist has albums
    if artist.albums:
        flash("Cannot delete artist with existsing albums.")
        return redirect(url_for("main.artist_details", artist_id=artist.id))

    db.session.delete(artist)
    db.session.commit()

    flash("Artist deleted.")
    return redirect(url_for("main.artists"))


@bp.route("/search", methods=["GET", "POST"])
def search():

    query = request.args.get("q", "").strip()

    limit = Config.SEARCH_LIMIT

    # Search artists
    artists = (
        db.session.query(Artists)
        .filter(Artists.name.ilike(f"%{query}%"))
        .order_by(Artists.name)
        .limit(limit)
        .all()
    )

    # Search albums
    albums = (
        db.session.query(Albums)
        .options(selectinload(Albums.artist), selectinload(Albums.genres))
        .join(Artists)
        .outerjoin(Albums.genres)
        .filter(
            or_(
                Albums.title.ilike(f"%{query}%"),
                Artists.name.ilike(f"%{query}%"),
                Albums.genres.any(Genres.name.ilike(f"%{query}%")),
                sa.cast(Albums.year, sa.String).ilike(f"%{query}%"),
                sa.cast(Albums.format, sa.String).ilike(f"%{query}%"),
            )
        )
        .distinct()
        .order_by(Albums.title.ilike(f"{query}%").desc(), Albums.title)
        .limit(limit)
        .all()
    )

    # Search tracks
    tracks = (
        db.session.query(Tracks)
        .options(selectinload(Tracks.album).selectinload(Albums.artist))
        .join(Albums)
        .join(Artists)
        .filter(
            or_(
                Tracks.title.ilike(f"%{query}%"),
                Albums.title.ilike(f"%{query}%"),
                Artists.name.ilike(f"%{query}%"),
            )
        )
        .order_by(Tracks.title)
        .limit(limit)
        .all()
    )

    if not any([artists, albums, tracks]):
        flash("No results found.")

    return render_template(
        "search_results.html",
        query=query,
        artists=artists,
        albums=albums,
        tracks=tracks,
    )
