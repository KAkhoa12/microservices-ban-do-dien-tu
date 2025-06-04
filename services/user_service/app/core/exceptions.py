from fastapi import HTTPException
from .response import Response,CodeEnum

class AuthException(Exception):
    def __init__(self, response: Response):
        self.response = response
        # Map CodeEnum to HTTP status codes
        status_code_map = {
            CodeEnum.UNAUTHORIZED: 401,
            CodeEnum.FORBIDDEN: 403,
            CodeEnum.NOT_FOUND: 404,
            CodeEnum.BAD_REQUEST: 400,
            CodeEnum.SERVER_ERROR: 500,
        }
        self.status = response.status
        self.code_code = status_code_map.get(response.status, 500)
        self.message = response.message
        self.data = response.data if hasattr(response, 'data') else None
        super().__init__(response.message)
    
    def to_dict(self):
        return {
            'status': self.status_code,
            'code': self.code,
            'message': self.message,
            'data': self.data
        }