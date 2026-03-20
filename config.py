import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    SECRET_KEY = (
        os.environ.get("SECRET_KEY") or "dev-key"
    )  # Change dev-key to random key for productive use
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "app.db")

    DISCOGS_API = "https://api.discogs.com/releases"

    ALBUMS_PER_PAGE = 25
    SEARCH_LIMIT = 25
