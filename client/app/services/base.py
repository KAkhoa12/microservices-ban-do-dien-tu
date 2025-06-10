import requests
import json
from ..response import Response
import os
# Base URL - Kong Gateway
API_URL = os.environ.get('API_URL', 'http://localhost:8000')  # URL của Kong Gateway

def handle_response(response):
    """Handle API response and return Response object"""
    try:
        if response.status_code == 200:
            response_data = response.json()
            return Response.from_dict(response_data).to_dict()
        else:
            # Handle non-200 status codes
            try:
                error_data = response.json()
                return Response(
                    status='error',
                    code=response.status_code,
                    message=error_data.get('detail', f'HTTP {response.status_code}'),
                    data=None
                ).to_dict()
            except:
                return Response(
                    status='error',
                    code=response.status_code,
                    message=f'HTTP {response.status_code}: {response.text}',
                    data=None
                ).to_dict()
    except Exception as e:
        return Response(status='error', code=500, message=str(e), data=None).to_dict()
