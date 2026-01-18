import os
import sys
import pytest

# Add project root to sys.path to allow importing website.app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from website.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # Set a dummy secret key for testing session functionality
    app.config['SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as client:
        yield client

def test_repack_wallpapers_production(client):
    """
    Test that /api/wallpapers/repack is forbidden in production mode.
    """
    # Ensure DEBUG is False for this test
    app.config['DEBUG'] = False
    response = client.get('/api/wallpapers/repack')
    assert response.status_code == 403

def test_repack_wallpapers_development(client):
    """
    Test that /api/wallpapers/repack is accessible in development mode.
    """
    # Ensure DEBUG is True for this test
    app.config['DEBUG'] = True
    # The script will fail because it's not a real request context,
    # but we should not get a 403. A 500 Internal Server Error is expected.
    response = client.get('/api/wallpapers/repack')
    assert response.status_code != 403
