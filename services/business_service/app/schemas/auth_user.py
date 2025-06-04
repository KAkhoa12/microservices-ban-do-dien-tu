from typing import Optional
from pydantic import BaseModel

class CurrentUser(BaseModel):
    user_id: int
    username: str
    user_role: str
    email: Optional[str] = None
    full_name: Optional[str] = None