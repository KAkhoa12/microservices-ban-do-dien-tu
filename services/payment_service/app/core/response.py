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
    def __init__(self,data=None, status = None,code = None, message = None):
        self.status = status
        self.code = code
        self.message = message
        self.data = data
    def to_dict(self):
        return {
            'status': self.status,
            'code': self.code,
            'message': self.message,
            'data': self.data
        }
