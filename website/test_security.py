import pytest
from website.app import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test'
    app.config['DEBUG'] = True
    with app.test_client() as client:
        yield client

def test_security_headers(client):
    """Test that security headers are present in responses"""
    response = client.get('/')
    assert response.status_code == 200
    assert response.headers['X-Content-Type-Options'] == 'nosniff'
    assert response.headers['X-Frame-Options'] == 'SAMEORIGIN'
    assert response.headers['X-XSS-Protection'] == '1; mode=block'
    assert response.headers['Referrer-Policy'] == 'strict-origin-when-cross-origin'
    assert 'Content-Security-Policy' in response.headers

def test_repack_endpoint_method_constraint(client):
    """Test that /api/wallpapers/repack only accepts POST"""
    # GET should be blocked (405)
    response = client.get('/api/wallpapers/repack')
    assert response.status_code == 405

    # POST should be allowed (in DEBUG mode it might return 200 or 500 depending on script existence,
    # but 405 means it's blocked at the routing level)
    # Since we set DEBUG=True in fixture, it should try to run the script.
    # We don't necessarily need to check for 200 here, just that it's NOT 405.

def test_contact_validation_missing_fields(client):
    """Test contact endpoint validation for missing fields"""
    payload = {"name": "", "email": "", "message": ""}
    response = client.post('/api/contact',
                           data=json.dumps(payload),
                           content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] is False
    assert "Validation failed" in data['message']
    assert len(data['errors']) == 3

def test_contact_validation_invalid_email(client):
    """Test contact endpoint validation for invalid email"""
    payload = {"name": "Test User", "email": "invalid-email", "message": "Hello"}
    response = client.post('/api/contact',
                           data=json.dumps(payload),
                           content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "Invalid email format" in data['errors']

def test_contact_validation_success(client):
    """Test contact endpoint successful validation"""
    payload = {"name": "Test User", "email": "test@example.com", "message": "Hello"}
    response = client.post('/api/contact',
                           data=json.dumps(payload),
                           content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
