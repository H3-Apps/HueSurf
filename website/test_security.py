import pytest
import json
from website.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret'
    # Force DEBUG to True for testing the repack endpoint
    app.config['DEBUG'] = True
    with app.test_client() as client:
        yield client

def test_security_headers_present(client):
    """Verify security headers (should fail until implemented)"""
    response = client.get('/')

    # We want these to BE PRESENT
    assert 'Content-Security-Policy' in response.headers
    assert response.headers.get('X-Content-Type-Options') == 'nosniff'
    assert response.headers.get('X-Frame-Options') == 'SAMEORIGIN'
    assert response.headers.get('X-XSS-Protection') == '1; mode=block'
    assert response.headers.get('Referrer-Policy') == 'strict-origin-when-cross-origin'

def test_repack_method_restriction(client):
    """Verify /api/wallpapers/repack only accepts POST (should fail until implemented)"""
    # GET should return 405 Method Not Allowed
    response = client.get('/api/wallpapers/repack')
    assert response.status_code == 405

def test_error_message_generic(client):
    """Verify error messages are generic (should fail until implemented)"""
    # Trigger an error in an endpoint by mocking or providing bad input
    # For example, calling repack with POST but it fails because of missing script
    response = client.post('/api/wallpapers/repack')

    if response.status_code == 500:
        data = response.get_json()
        # It should return a generic message.
        assert "Failed to repack wallpapers" in data['message'] or "internal error" in data['message']
        # And it should NOT contain the specific exception details (like [Errno 2] or result.stderr)
        assert "[Errno" not in data['message']
        assert "error" not in data
