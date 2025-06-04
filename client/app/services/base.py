import requests
import json
from ..response import Response

# Base URL - Kong Gateway
API_URL = "http://localhost:8000"  # URL của Kong Gateway

def handle_response(response):
    """Handle API response and return Response object"""
    try:
        response_data = response.json()
        return Response.from_dict(response_data).to_dict()
    except Exception as e:
        return Response(status='error', code=500, message=str(e), data=None).to_dict()
