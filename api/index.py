"""
AI Customer Service - Vercel Serverless Adapter
Wraps the FastAPI app from api/main.py for Vercel Python runtime
"""
import os
import sys

# Ensure project root is in path (for services/ imports)
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import the FastAPI app from api/main.py
from api.main import app

# Vercel @vercel/python auto-detects FastAPI 'app' directly
