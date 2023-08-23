from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserResponse(BaseModel):
    id: int
    name: Optional[str] = None
    email: Optional[str] = None
    line_id: Optional[str] = None
    created_at: Optional[str] = None
    pinecone_index: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
