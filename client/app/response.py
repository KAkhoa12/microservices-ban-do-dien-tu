from enum import Enum

class CodeEnum(Enum):
    SUCCESS = 200
    BAD_REQUEST = 400
    SERVER_ERROR = 500
    NOT_FOUND = 404
    UNAUTHORIZED = 401
    FORBIDDEN = 403

class StatusEnum(Enum):
    SUCCESS = 'success'
    ERROR = 'error'

class Response:
    def __init__(self, data=None, status=None, code=None, message=None):
        self.status = status
        self.code = code
        self.message = message
        self.data = data

    @classmethod
    def from_dict(cls, response_dict):
        return cls(
            data=response_dict.get('data'),
            status=response_dict.get('status'),
            code=response_dict.get('code'),
            message=response_dict.get('message')
        )

    def is_success(self):
        """Check if the response is successful"""
        return self.status == StatusEnum.SUCCESS.value and self.code == CodeEnum.SUCCESS.value

    def to_dict(self):
        """Convert Response object to dictionary"""
        return {
            'status': self.status,
            'code': self.code,
            'message': self.message,
            'data': self.data
        }

    def get_payload(self):
        """Get payload from response data"""
        if isinstance(self.data, dict):
            return self.data.get('items', [])
        return []
