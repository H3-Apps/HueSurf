import os
import sys

# Add website to path so we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'website')))

# Set dummy environment variables
os.environ['SECRET_KEY'] = 'test-secret'
os.environ['FLASK_ENV'] = 'development'

from app import app

client = app.test_client()

def test_repack():
    response = client.post("/api/wallpapers/repack")
    print(f"POST /api/wallpapers/repack status: {response.status_code}")
    print(f"Response: {response.data.decode()}")

if __name__ == "__main__":
    test_repack()
