import requests
from pathlib import Path
from config import Config
from app.models import Tracks


def download_discogs_cover(discogs_id, album_id):
    url = f"{Config.DISCOGS_API}{discogs_id}"

    headers = {"User-Agent": "MusicCollectionApp/1.0"}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return None

    data = response.json()

    if not data.get("images"):
        return None

    cover_url = data["images"][0]["uri"]

    image_response = requests.get(cover_url)

    filename = f"album_{album_id}.jpg"
    path = Path("app/static/covers") / filename

    with open(path, "wb") as f:
        f.write(image_response.content)

    return f"covers/{filename}"


def fetch_discogs_data(discogs_id):

    headers = {"User-Agent": "MusicCollectionApp/1.0"}

    response = requests.get(f"{Config.DISCOGS_API}{discogs_id}", headers=headers)

    if response.status_code != 200:
        return None

    return response.json()


def extract_tracks(data):
    tracks = []

    if "tracklist" not in data:
        return tracks

    for index, t in enumerate(data["tracklist"], start=1):

        if t.get("type_") != "track":
            continue

        duration = t.get("duration", "")
        seconds = parse_duration(duration)

        tracks.append(
            {
                "title": t.get("title"),
                "track_number": index,
                "duration_seconds": seconds,
            }
        )

    return tracks


def parse_duration(duration_str):
    if not duration_str or ":" not in duration_str:
        return None

    try:
        minutes, seconds = duration_str.split(":")
        return int(minutes) * 60 + int(seconds)
    except ValueError:
        return None


def import_tracks(album, track_data_list, db):
    for t in track_data_list:
        track = Tracks(
            album=album,
            title=t["title"],
            track_number=t["track_number"],
            duration_seconds=t["duration_seconds"],
        )
        db.session.add(track)
