from enum import Enum
from pydantic import BaseModel
from typing import Any, Optional

class StatusEnum(str, Enum):
    SUCCESS = "success"
    ERROR = "error"

class CodeEnum(int, Enum):
    SUCCESS = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500

class Response(BaseModel):
    status: StatusEnum
    code: CodeEnum
    message: str
    data: Optional[Any] = None
