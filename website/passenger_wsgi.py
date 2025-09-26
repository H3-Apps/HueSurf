#!/usr/bin/python3
import sys
import os

# Add your project directory to sys.path
sys.path.insert(0, os.path.dirname(__file__))

# Import your Flask application
from app import app as application

# Set environment variables for production
os.environ["FLASK_ENV"] = "production"

# Ensure the application is accessible
if __name__ == "__main__":
    application.run()
