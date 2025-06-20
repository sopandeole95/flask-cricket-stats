import pytest
import os
import sys

# Ensure project root is in sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from app import create_app, db

from app import create_app, db

@pytest.fixture
def app():
    # Create a Flask app configured for testing
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    # Returns a test client for the app
    return app.test_client()
