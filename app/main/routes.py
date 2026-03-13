import sqlalchemy as sa
from flask import render_template, flash, redirect, url_for, request, current_app
from app import db
from app.main import bp


@bp.route("/", methods=["GET"])
@bp.route("/index", methods=["GET"])
def index():
    return render_template("index.html", title="Home")


@bp.route("/albums", methods=["GET"])
def albums():
    return render_template("albums.html", title="Albums")


@bp.route("/album_details/<albumname>", methods=["GET"])
def album_details(albumname):
    return render_template("album_details.html")


@bp.route("/add_album", methods=["GET", "POST"])
def add_album():
    return render_template("add_album.html", title="Add Album")


@bp.route("/artists", methods=["GET"])
def artists():
    return render_template("artists.html", title="Artists")


@bp.route("/artist_details/<artistname>", methods=["GET"])
def artist_details(artistname):
    return render_template("artist_details.html")


@bp.route("/search", methods=["GET", "POST"])
def search():
    return render_template("search.html", title="Search")
