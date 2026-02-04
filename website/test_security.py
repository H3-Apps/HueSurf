import pytest
from website.app import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DEBUG'] = True
    with app.test_client() as client:
        yield client

def test_security_headers(client):
    """Test that security headers are present"""
    response = client.get('/')
    assert response.headers.get('X-Content-Type-Options') == 'nosniff'
    assert response.headers.get('X-Frame-Options') == 'SAMEORIGIN'
    assert response.headers.get('X-XSS-Protection') == '1; mode=block'
    assert response.headers.get('Referrer-Policy') == 'strict-origin-when-cross-origin'
    assert 'Content-Security-Policy' in response.headers

def test_repack_method(client):
    """Test that repack only works with POST"""
    response = client.get('/api/wallpapers/repack')
    assert response.status_code == 405

def test_contact_validation(client):
    """Test contact form validation"""
    # Test with empty data
    response = client.post('/api/contact',
                           data=json.dumps({}),
                           content_type='application/json')
    assert response.status_code == 400

    # Test with invalid name
    response = client.post('/api/contact',
                           data=json.dumps({"name": "A", "email": "test@example.com", "message": "Valid message length"}),
                           content_type='application/json')
    assert response.status_code == 400

    # Test with invalid email
    response = client.post('/api/contact',
                           data=json.dumps({"name": "Valid Name", "email": "invalid-email", "message": "Valid message length"}),
                           content_type='application/json')
    assert response.status_code == 400

    # Test with too short message
    response = client.post('/api/contact',
                           data=json.dumps({"name": "Valid Name", "email": "test@example.com", "message": "Short"}),
                           content_type='application/json')
    assert response.status_code == 400

    # Test with valid data
    response = client.post('/api/contact',
                           data=json.dumps({"name": "Valid Name", "email": "test@example.com", "message": "This is a valid message length"}),
                           content_type='application/json')
    assert response.status_code == 200

def test_main_routes(client):
    """Test that main routes still work"""
    routes = ['/', '/features', '/download', '/about', '/wallpapers']
    for route in routes:
        response = client.get(route)
        assert response.status_code == 200
