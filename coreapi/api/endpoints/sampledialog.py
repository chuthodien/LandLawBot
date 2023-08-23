from fastapi import APIRouter, Depends, File, Form, HTTPException
from typing import Optional, List
from api.dto import SampleDialogResponse
from sqlalchemy.orm import Session
from database import AiAgent, SampleDialog, get_db, User
from middleware import get_current_user

router = APIRouter()

# Get all sample dialogs
@router.get("/sampledialogs")
async def read_sampledialogs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    sample_dialogs = db.query(SampleDialog).offset(skip).limit(limit).all()

    if current_user != 'admin':
        raise HTTPException(status_code=403 , detail="Access denied")
    
    response = []
    for sample_dialog in sample_dialogs:
        response.append(SampleDialogResponse(
            id=sample_dialog.id,
            agent_id=sample_dialog.agent_id,
            content=sample_dialog.content,
        ))
    return response

# Get sample dialog by id
@router.get("/sampledialogs/{sample_dialog_id}")
async def read_sample_dialog_by_id(
    sample_dialog_id:int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    sample_dialog = db.query(SampleDialog).filter(SampleDialog.id == sample_dialog_id).first()
    ai_agent = db.query(AiAgent).filter(AiAgent.id == sample_dialog.agent_id).first()
    user = db.query(User).filter(User.id == ai_agent.user_id).first()

    if user.name != current_user:
        raise HTTPException(status_code=403 , detail="Access denied")
    
    if not sample_dialog:
        raise HTTPException(status_code=404, detail="Sample Dialog not found")
    
    return SampleDialogResponse(
        id=sample_dialog.id,
        agent_id=sample_dialog.agent_id,
        content=sample_dialog.content,
    )

# Get list sample dialog by aiagent id
@router.get("/sampledialogs/aiagent/{aiagent_id}")
async def read_sample_dialog_by_id(
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
    
    sample_dialogs = db.query(SampleDialog).filter(SampleDialog.agent_id == aiagent_id).offset(skip).limit(limit).all()
    if not sample_dialogs:
        raise HTTPException(status_code=404, detail="Sample Dialog not found")
    
    response = []
    for sample_dialog in sample_dialogs:
        response.append(SampleDialogResponse(
            id=sample_dialog.id,
            agent_id=sample_dialog.agent_id,
            content=sample_dialog.content,
        ))
    return response

# Create sample dialogs
@router.post("/sampledialogs/create/{agent_id}")
async def create_sampledialogs(
    agent_id: int,
    content: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    ai_agent = db.query(AiAgent).filter(AiAgent.id == agent_id).first()
    user = db.query(User).filter(User.id == ai_agent.user_id).first()

    if user.name != current_user:
        raise HTTPException(status_code=403 , detail="Access denied")
    
    if not ai_agent:
        raise HTTPException(status_code=404, detail="Ai Agent not found")
    
    sample_dialog = SampleDialog(
        agent_id=agent_id,
        content=content,
    )
    db.add(sample_dialog)
    db.commit()
    db.refresh(sample_dialog)

    return SampleDialogResponse(
        id=sample_dialog.id,
        agent_id=sample_dialog.agent_id,
        content=sample_dialog.content,
    )

# Update sample dialogs
@router.put("/sampledialogs/update/{sampledialg_id}")
async def update_sampledialog(
    sampledialg_id: int,
    content: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    sample_dialog = db.query(SampleDialog).filter(SampleDialog.id == sampledialg_id).first()
    ai_agent = db.query(AiAgent).filter(AiAgent.id == sample_dialog.agent_id).first()
    user = db.query(User).filter(User.id == ai_agent.user_id).first()

    if user.name != current_user:
        raise HTTPException(status_code=403 , detail="Access denied")

    if not sample_dialog:
        raise HTTPException(status_code=404, detail="Sample dialog not found")
    
    if content and content != sample_dialog.content:
        sample_dialog.content = content
        
        db.merge(sample_dialog)
        db.commit()
        db.refresh(sample_dialog)

    return SampleDialogResponse(
        id=sample_dialog.id,
        agent_id=sample_dialog.agent_id,
        content=sample_dialog.content,
    )

# Delete sample dialogs
@router.delete("/sampledialogs/delete/{sampledialg_id}")
async def delete_sampledialog(
    sampledialg_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    sample_dialog = db.query(SampleDialog).filter(SampleDialog.id == sampledialg_id).first()
    ai_agent = db.query(AiAgent).filter(AiAgent.id == sample_dialog.agent_id).first()
    user = db.query(User).filter(User.id == ai_agent.user_id).first()

    if user.name != current_user:
        raise HTTPException(status_code=403 , detail="Access denied")
    
    if not sample_dialog:
        raise HTTPException(status_code=404, detail="Sample dialog not found")
    
    db.delete(sample_dialog)
    db.commit()

    return {"result": "delete oke"}