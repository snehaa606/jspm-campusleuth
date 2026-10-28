import os
import sys

# Ensure root directory is on the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Expose app for Vercel WSGI
app = app
