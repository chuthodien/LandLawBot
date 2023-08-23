from typing import Optional
from .audio_encoding import AudioEncoding
from .model import BaseModel


class InputAudioConfig(BaseModel):
    sampling_rate: int
    audio_encoding: AudioEncoding
    chunk_size: int
    is_safari: bool
    downsampling: Optional[int] = None
    

class OutputAudioConfig(BaseModel):
    sampling_rate: int
    audio_encoding: AudioEncoding