import unittest

from app import create_app, db
from app.models import Albums, Artists, Tracks
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"


class AlbumModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_album(self):
        # Create an artist
        testartist = Artists(
            name="testartist", country="testcountry", year_of_founding=1984
        )
        db.session.add(testartist)

        # Create four tracks
        t1 = Tracks(title="testtrack_1", track_number=1, duration_seconds=66)
        t2 = Tracks(title="testtrack_2", track_number=2, duration_seconds=36)
        t3 = Tracks(title="testtrack_3", track_number=3, duration_seconds=92)
        t4 = Tracks(title="testtrack_4", track_number=4, duration_seconds=87)
        db.session.add_all([t1, t2, t3, t4])

        # Create an Album
        a = Albums(
            title="testalbum",
            year=1990,
            format="vinyl",
            label="testlabel",
            artist=testartist,
            tracks=[t1, t2, t3, t4],
        )
        db.session.add(a)
        db.session.commit()


if __name__ == "__main__":
    unittest.main(verbosity=2)
