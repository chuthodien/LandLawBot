from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from api.dto.sampledialog import SampleDialogResponse
from api.dto.samplevoice import SampleVoiceResponse

class AiAgentResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    name: Optional[str] = None
    introduction: Optional[str] = None
    created_at: Optional[str] = None
    pdf_file: Optional[str] = None
    icon_file: Optional[str] = None
    voice_model_file: Optional[str] = None
    pinecone_namespace: Optional[str] = None
    age: Optional[int] = None
    first_person_pronoun: Optional[str] = None
    second_person_pronoun: Optional[str] = None
    activity: Optional[str] = None
    hobbies: Optional[str] = None
    occupation: Optional[str] = None
    speaking_style: Optional[str] = None

class AiAgentResponseDetail(BaseModel):
    id: int
    user_id: Optional[int] = None
    name: Optional[str] = None
    introduction: Optional[str] = None
    created_at: Optional[str] = None
    pdf_file: Optional[str] = None
    icon_file: Optional[str] = None
    voice_model_file: Optional[str] = None
    pinecone_namespace: Optional[str] = None
    age: Optional[int] = None
    first_person_pronoun: Optional[str] = None
    second_person_pronoun: Optional[str] = None
    activity: Optional[str] = None
    hobbies: Optional[str] = None
    occupation: Optional[str] = None
    speaking_style: Optional[str] = None
    sample_dialog: List[SampleDialogResponse] = None
    sample_voice: List[SampleVoiceResponse] = None