from flask import Blueprint

bp = Blueprint("services", __name__)

from app.services import discogs
