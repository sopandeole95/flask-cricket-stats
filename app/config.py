import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # SQLite file will live next to your code
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or f"sqlite:///{os.path.join(basedir, '..', 'cricket_stats.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "you-will-want-to-change-this")
