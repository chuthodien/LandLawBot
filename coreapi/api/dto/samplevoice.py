from fastapi import File, UploadFile
from pydantic import BaseModel
from typing import Optional

class SampleVoiceResponse(BaseModel):
    id: int
    agent_id: Optional[int] = None
    file: Optional[str] = None

class SampleVoiceFile(BaseModel):
    id: int = None
    file: Optional[UploadFile] = File(None)
