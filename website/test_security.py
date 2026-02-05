import pytest
import re
from website.app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["DEBUG"] = True  # Enable for repack testing
    app.config["SECRET_KEY"] = "test-secret-key"
    with app.test_client() as client:
        yield client

def test_security_headers(client):
    """Test that security headers are present in responses"""
    response = client.get("/")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "SAMEORIGIN"
    assert response.headers["X-XSS-Protection"] == "1; mode=block"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "Content-Security-Policy" in response.headers

def test_repack_endpoint_methods(client):
    """Test that /api/wallpapers/repack only accepts POST"""
    # GET should fail (405 Method Not Allowed)
    response = client.get("/api/wallpapers/repack")
    assert response.status_code == 405

    # POST should be attempted (might fail 500 if subprocess fails, but 405 is what we're checking for GET)
    # We don't necessarily want it to succeed in tests without proper setup,
    # but we want to ensure it doesn't return 405.
    response = client.post("/api/wallpapers/repack")
    assert response.status_code != 405

def test_repack_info_leakage(client):
    """Test that /api/wallpapers/repack doesn't leak info on failure"""
    # Force a failure if possible or just check the response structure
    # In this environment, it might actually work or fail.
    # Either way, it should NOT have 'output' or 'error' keys.
    response = client.post("/api/wallpapers/repack")
    data = response.get_json()
    assert "output" not in data
    assert "error" not in data

def test_contact_validation_missing_fields(client):
    """Test contact endpoint with missing fields"""
    response = client.post("/api/contact", json={"name": "Test"})
    assert response.status_code == 400
    assert response.get_json()["success"] is False
    assert "required" in response.get_json()["message"]

def test_contact_validation_invalid_email(client):
    """Test contact endpoint with invalid email"""
    response = client.post("/api/contact", json={
        "name": "Test User",
        "email": "invalid-email",
        "message": "Hello"
    })
    assert response.status_code == 400
    assert response.get_json()["success"] is False
    assert "email" in response.get_json()["message"].lower()

def test_contact_validation_success(client):
    """Test contact endpoint with valid data"""
    response = client.post("/api/contact", json={
        "name": "Test User",
        "email": "test@example.com",
        "message": "This is a valid message"
    })
    assert response.status_code == 200
    assert response.get_json()["success"] is True

def test_contact_validation_length(client):
    """Test contact endpoint with overly long input"""
    response = client.post("/api/contact", json={
        "name": "A" * 101,
        "email": "test@example.com",
        "message": "Hello"
    })
    assert response.status_code == 400
    assert "exceeds" in response.get_json()["message"]
