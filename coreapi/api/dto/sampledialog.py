from pydantic import BaseModel
from typing import Optional

class SampleDialogResponse(BaseModel):
    id: int
    agent_id: Optional[int] = None
    content: Optional[str] = None

class SampleDialogResponseCreate(BaseModel):
    agent_id: Optional[int] = None
    content: Optional[str] = None