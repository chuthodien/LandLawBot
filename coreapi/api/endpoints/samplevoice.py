import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Optional
from api.dto import SampleVoiceResponse
from sqlalchemy.orm import Session
from database import AiAgent, SampleVoice, get_db, User
from middleware import get_current_user

router = APIRouter()

base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
assets_dir = "assets"
voice_dir = os.path.join(assets_dir, "voice")
if not os.path.exists(voice_dir):
    os.mkdir(voice_dir)

# Get all sample voice
@router.get("/samplevoices")
async def read_samplevoices(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    sample_voices = db.query(SampleVoice).offset(skip).limit(limit).all()

    if current_user != 'admin':
        raise HTTPException(status_code=403 , detail="Access denied")
    
    response = []
    for sample_voice in sample_voices:
        response.append(SampleVoiceResponse(
            id=sample_voice.id,
            agent_id=sample_voice.agent_id,
            file=sample_voice.file
        ))
    return response

# Get sample voice by id
@router.get("/samplevoices/{sample_voice_id}")
async def read_sample_voice_by_id(
    sample_voice_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    sample_voice = db.query(SampleVoice).filter(SampleVoice.id == sample_voice_id).first()
    ai_agent = db.query(AiAgent).filter(AiAgent.id == sample_voice.agent_id).first()
    user = db.query(User).filter(User.id == ai_agent.user_id).first()

    if user.name != current_user:
        raise HTTPException(status_code=403 , detail="Access denied")
    
    if not sample_voice:
        raise HTTPException(status_code=404, detail="Sample voice dialog not found")
    
    return SampleVoiceResponse(
        id=sample_voice.id,
        agent_id=sample_voice.agent_id,
        file=sample_voice.file
    )

# Get list sample voice by aiagent id
@router.get("/samplevoices/aiagent/{aiagent_id}")
async def read_sample_voice_by_aiagent_id(
    aiagent_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    ai_agent = db.query(AiAgent).filter(AiAgent.id == aiagent_id).first()

    user = db.query(User).filter(User.id == ai_agent.user_id).first()

    if user.name != current_user:
        raise HTTPException(status_code=403 , detail="Access denied")
    
    if not ai_agent:
        raise HTTPException(status_code=404, detail="Ai agent not found")
    
    sample_voices = db.query(SampleVoice).filter(SampleVoice.agent_id == aiagent_id).offset(skip).limit(limit).all()
    if not sample_voices:
        raise HTTPException(status_code=404, detail="Sample voice not found")
    
    response = []
    for sample_voice in sample_voices:
        response.append(SampleVoiceResponse(
            id = sample_voice.id,
            agent_id = sample_voice.agent_id,
            file = sample_voice.file
        ))
    return response

# Create sample voice
@router.post("/samplevoices/create/{agent_id}")
async def create_samplevoice(
    agent_id: int,
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    ai_agent = db.query(AiAgent).filter(AiAgent.id == agent_id).first()
    if not ai_agent:
        raise HTTPException(status_code=404, detail="Ai Agent not found")
    
    if file:
        sample_voice_path_agent_name = os.path.join(assets_dir, "voice", str(agent_id))
        if not os.path.exists(sample_voice_path_agent_name):
            os.mkdir(sample_voice_path_agent_name)
        sample_voice_path = os.path.join(assets_dir, "voice", str(agent_id), file.filename)
        with open(sample_voice_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        sample_voice_url = "/" + sample_voice_path.replace("\\", "/")

        sample_voice = SampleVoice(
            agent_id=agent_id,
            file=sample_voice_url,
        )

        db.add(sample_voice)
        db.commit()
        db.refresh(sample_voice)

        return SampleVoiceResponse(
            id=sample_voice.id,
            agent_id=sample_voice.agent_id,
            file=sample_voice.file,
        )

# Update sample voice
@router.put("/samplevoices/update/{sample_voice_id}")
async def update_sample_voice(
    sample_voice_id: int,
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    sample_voice = db.query(SampleVoice).filter(SampleVoice.id == sample_voice_id).first()

    ai_agent = db.query(AiAgent).filter(AiAgent.id == sample_voice.agent_id).first()
    user = db.query(User).filter(User.id == ai_agent.user_id).first()

    if user.name != current_user:
        raise HTTPException(status_code=403 , detail="Access denied")
    
    if not sample_voice:
        raise HTTPException(status_code=404, detail="Sample dialog not found")
    
    if file:
        sample_voice_path_agent_name = os.path.join(assets_dir, "voice", str(sample_voice.agent_id))
        if not os.path.exists(sample_voice_path_agent_name):
            os.mkdir(sample_voice_path_agent_name)
        sample_voice_path = os.path.join(assets_dir, "voice", str(sample_voice.agent_id), file.filename)
        with open(sample_voice_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        sample_voice_url = "/" + sample_voice_path.replace("\\", "/")

        sample_voice.file = sample_voice_url

        db.merge(sample_voice)
        db.commit()
        db.refresh(sample_voice)

        return SampleVoiceResponse(
            id=sample_voice.id,
            agent_id=sample_voice.agent_id,
            file=sample_voice.file,
        )

# Delete sample voice
@router.delete("/samplevoices/delete/{sample_voice_id}")
async def delete_samplevoice(
    sample_voice_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    sample_voice = db.query(SampleVoice).filter(SampleVoice.id == sample_voice_id).first()
    ai_agent = db.query(AiAgent).filter(AiAgent.id == sample_voice.agent_id).first()
    user = db.query(User).filter(User.id == ai_agent.user_id).first()

    if user.name != current_user:
        raise HTTPException(status_code=403 , detail="Access denied")
    
    if not sample_voice:
        raise HTTPException(status_code=404, detail="Sample voice not found")
    
    db.delete(sample_voice)
    db.commit()

    return {"result": "delete success"}