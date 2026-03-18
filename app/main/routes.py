import sqlalchemy as sa
from flask import render_template, flash, redirect, url_for, request, current_app, g
from app import db
from app.main import bp
from app.main.forms import AddAlbumForm
from app.models import (
    Artists,
    Albums,
    Tracks,
    Genres,
)


@bp.route("/", methods=["GET"])
@bp.route("/index", methods=["GET"])
def index():
    return render_template("index.html", title="Home")


@bp.route("/albums", methods=["GET"])
def albums():
    page = request.args.get("page", 1, type=int)
    albums = db.paginate(
        Albums.title,
        page=page,
        per_page=current_app.config["ALBUMS_PER_PAGE"],
        error_out=False,
    )
    next_url = url_for("main.albums", page=albums.next_num) if albums.has_next else None
    prev_url = url_for("main.albums", page=albums.prev_num) if albums.has_prev else None
    return render_template(
        "albums.html",
        title="Albums",
        albums=albums.items,
        next_url=next_url,
        prev_url=prev_url,
    )


@bp.route("/album_details/<albumname>", methods=["GET"])
def album_details(albumname):
    return render_template("album_details.html")


@bp.route("/add_album", methods=["GET", "POST"])
def add_album():
    form = AddAlbumForm()

    genres = Genres.query.order_by(Genres.name).all()
    artists = Artists.query.order_by(Artists.name).all()

    form.genre.choices = [(0, "---")] + [
        (g.id, g.name) for g in genres
    ]  # Filling genre dropdown menu, starting with ---
    form.artist.choices = [(0, "---")] + [
        (g.id, g.name) for g in artists
    ]  # Filling artists dropdown menu, starting with ---

    if form.validate_on_submit():

        # Artist handling
        if form.new_artist.data:
            artist = Artists(name=form.new_artist.data)
            db.session.add(artist)
            db.session.flush()
        else:
            artist = db.session.get(Artists, form.artist.data)

        # Genre handling
        if form.new_genre.data:
            genre = Genres(name=form.new_genre.data)
            db.session.add(genre)
            db.session.flush()
        else:
            genre = db.session.get(Genres, form.genre.data)

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
        return redirect(url_for("main.edit tracks", album_id=new_album.id))

    return render_template("add_album.html", title="Add Album", form=form)


@bp.route("/album/<int:album_id>/tracks", methods=["GET", "POST"])
def edit_tracks(album_id):
    album = db.session.get(Albums, album_id)

    tracks = sorted(album.tracks, key=lambda t: t.track_number)

    return render_template(
        "edit_tracks.html", title=album.title, album=album, tracks=tracks
    )


@bp.route("/artists", methods=["GET"])
def artists():
    return render_template("artists.html", title="Artists")


@bp.route("/artist_details/<artistname>", methods=["GET"])
def artist_details(artistname):
    return render_template("artist_details.html")


@bp.route("/search", methods=["GET", "POST"])
def search():
    return render_template("search.html", title="Search")
