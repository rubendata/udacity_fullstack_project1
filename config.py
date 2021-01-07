import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True
FLASK_DEBUG=True
FLASK_ENV='development'
SQL_ALCHEMY_TRACK_MODIFICATIONS=False

# Connect to the database


# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/fyyur'
