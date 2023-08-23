import datetime
import json
import os
import shutil
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from typing import Optional, List
from api.dto import SampleVoiceResponse, SampleDialogResponse, AiAgentResponse, AiAgentResponseDetail
from sqlalchemy.orm import Session
from database import User, AiAgent, SampleDialog, SampleVoice, get_db
from middleware import get_current_user
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

SERVER_URL = os.getenv('SERVER_URL')

base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
assets_dir = "assets"
assets_path = os.path.join(base_path, assets_dir)
avatar_dir = os.path.join(assets_dir, "avatar")
model_dir = os.path.join(assets_dir, "model")
pdf_dir = os.path.join(assets_dir, "pdf")
voice_dir = os.path.join(assets_dir, "voice")
if not os.path.exists(assets_dir):
    os.mkdir(assets_dir)
if not os.path.exists(avatar_dir):
    os.mkdir(avatar_dir)
if not os.path.exists(model_dir):
    os.mkdir(model_dir)
if not os.path.exists(pdf_dir):
    os.mkdir(pdf_dir)
if not os.path.exists(voice_dir):
    os.mkdir(voice_dir)

# Get all ai agent
@router.get("/aiagents")
async def read_aiagents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    aiAgents = db.query(AiAgent).offset(skip).limit(limit).all()

    if current_user != 'admin':
        raise HTTPException(status_code=403 , detail="Access denied")
    
    response = []
    for aiAgent in aiAgents:
        pdf_path = None
        icon_path = None
        model_path = None
        if aiAgent.pdf_file:
            pdf_path = SERVER_URL + aiAgent.pdf_file
        if aiAgent.icon_file:
            icon_path = SERVER_URL + aiAgent.icon_file
        if aiAgent.voice_model_file:
            model_path = SERVER_URL + aiAgent.voice_model_file
        response.append(AiAgentResponse(
            id = aiAgent.id,
            user_id = aiAgent.user_id,
            name = aiAgent.name,
            introduction = aiAgent.introduction,
            created_at = str(aiAgent.created_at),
            pdf_file = pdf_path,
            icon_file = icon_path,
            voice_model_file = model_path,
            pinecone_namespace = aiAgent.pinecone_namespace,
            age = aiAgent.age,
            first_person_pronoun = aiAgent.first_person_pronoun,
            second_person_pronoun = aiAgent.second_person_pronoun,
            activity = aiAgent.activity,
            hobbies = aiAgent.hobbies,
            occupation = aiAgent.occupation,
            speaking_style = aiAgent.speaking_style,
        ))
    return response

# Get list ai agent by user_id
@router.get("/aiagents/user/{user_id}")
async def get_aiagent_by_user_id(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    
    if user.name != current_user:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    ai_agents = db.query(AiAgent).filter(AiAgent.user_id == user_id).offset(skip).limit(limit).all()
    response = []
    for ai_agent in ai_agents:
        icon_path = None
        if ai_agent.icon_file:
            icon_path = SERVER_URL + ai_agent.icon_file

        voice_model_path = None
        if ai_agent.voice_model_file:
            voice_model_path = SERVER_URL + ai_agent.voice_model_file
        
        pdf_path = None
        if ai_agent.pdf_file:
            pdf_path = SERVER_URL + ai_agent.pdf_file

        sample_dialogs = db.query(SampleDialog).filter(SampleDialog.agent_id == ai_agent.id).offset(skip).limit(limit).all()
        list_sample_dialogs = []
        for sampleDialog in sample_dialogs:
            list_sample_dialogs.append(SampleDialogResponse(
                id=sampleDialog.id,
                agent_id=sampleDialog.agent_id,
                content=sampleDialog.content,
            ))
        
        sample_voices = db.query(SampleVoice).filter(SampleVoice.agent_id == ai_agent.id).offset(skip).limit(limit).all()
        list_sample_voices = []
        for sample_voice in sample_voices:
            file_path = None
            if sample_voice.file:
                file_path = SERVER_URL + sample_voice.file
            list_sample_voices.append(SampleVoiceResponse(
                id = sample_voice.id,
                agent_id = sample_voice.agent_id,
                file = file_path
            ))

        response.append(AiAgentResponseDetail(
            id = ai_agent.id,
            user_id = ai_agent.user_id,
            name = ai_agent.name,
            introduction = ai_agent.introduction,
            created_at = str(ai_agent.created_at),
            pdf_file = pdf_path,
            icon_file = icon_path,
            voice_model_file = voice_model_path,
            pinecone_namespace = ai_agent.pinecone_namespace,
            age = ai_agent.age,
            first_person_pronoun = ai_agent.first_person_pronoun,
            second_person_pronoun = ai_agent.second_person_pronoun,
            activity = ai_agent.activity,
            hobbies = ai_agent.hobbies,
            occupation = ai_agent.occupation,
            speaking_style = ai_agent.speaking_style,
            sample_dialog = list_sample_dialogs,
            sample_voice = list_sample_voices
        ))
    
    return response

# Get ai agent by id
@router.get("/aiagents/{agent_id}")
async def read_aiagent_by_id(
    agent_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    ai_agent = db.query(AiAgent).filter(AiAgent.id == agent_id).first()
    user = db.query(User).filter(User.id == ai_agent.user_id).first()

    if user.name != current_user:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not ai_agent:
        raise HTTPException(status_code=404, detail="Ai agent not found")
    
    sample_dialogs = db.query(SampleDialog).filter(SampleDialog.agent_id == ai_agent.id).offset(skip).limit(limit).all()
    list_sample_dialogs = []
    for sample_dialog in sample_dialogs:
        list_sample_dialogs.append(SampleDialogResponse(
            id=sample_dialog.id,
            agent_id=sample_dialog.agent_id,
            content=sample_dialog.content,
        ))
    
    sampleVoices = db.query(SampleVoice).filter(SampleVoice.agent_id == ai_agent.id).offset(skip).limit(limit).all()
    list_sample_voices = []
    for sample_voice in sampleVoices:
        file_path = None
        if sample_voice.file:
            file_path = SERVER_URL + sample_voice.file
        list_sample_voices.append(SampleVoiceResponse(
            id = sample_voice.id,
            agent_id = sample_voice.agent_id,
            file = file_path
        ))
    
    icon_path = None
    if ai_agent.icon_file:
        icon_path = SERVER_URL + ai_agent.icon_file

    voice_model_path = None
    if ai_agent.voice_model_file:
        voice_model_path = SERVER_URL + ai_agent.voice_model_file
    
    pdf_path = None
    if ai_agent.pdf_file:
        pdf_path = SERVER_URL + ai_agent.pdf_file

    return AiAgentResponseDetail(
        id = ai_agent.id,
        user_id = ai_agent.user_id,
        name = ai_agent.name,
        introduction = ai_agent.introduction,
        created_at = str(ai_agent.created_at),
        pdf_file = pdf_path,
        icon_file = icon_path,
        voice_model_file = voice_model_path,
        pinecone_namespace = ai_agent.pinecone_namespace,
        age = ai_agent.age,
        first_person_pronoun = ai_agent.first_person_pronoun,
        second_person_pronoun = ai_agent.second_person_pronoun,
        activity = ai_agent.activity,
        hobbies = ai_agent.hobbies,
        occupation = ai_agent.occupation,
        speaking_style = ai_agent.speaking_style,
        sample_dialog = list_sample_dialogs,
        sample_voice = list_sample_voices
    )

# Post ai agent
@router.post("/aiagents/create/{user_id}")
async def create_aiagent(
    user_id: int,
    name: Optional[str] = Form(None),
    introduction: Optional[str] = Form(None),
    pdf_file: Optional[UploadFile] = File(None),
    icon_file: Optional[UploadFile] = File(None),
    voice_model_file: Optional[UploadFile] = File(None),
    pinecone_namespace: Optional[str] = Form(None),
    age: Optional[int] = Form(None),
    first_person_pronoun: Optional[str] = Form(None),
    second_person_pronoun: Optional[str] = Form(None),
    activity: Optional[str] = Form(None),
    hobbies: Optional[str] = Form(None),
    occupation: Optional[str] = Form(None),
    speaking_style: Optional[str] = Form(None),
    sample_dialogs: Optional[str] = Form(None),
    sample_voices: List[Optional[UploadFile]] = File(None),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    ai_agent_db = db.query(AiAgent).filter(AiAgent.name == name and AiAgent.user_id == user_id).first()
    if ai_agent_db:
        raise HTTPException(status_code=409, detail="Name already exists")
    
    ai_agent_last = db.query(AiAgent).order_by(AiAgent.id.desc()).first()
    agent_id = 1
    if ai_agent_last:
        agent_id = ai_agent_last.id + 1
    
    pdf_file_url = None
    if pdf_file is not None:
        if len(pdf_file.filename) > 0:
            pdf_file_path_agent_name = os.path.join(assets_dir, "pdf", str(agent_id))
            if not os.path.exists(pdf_file_path_agent_name):
                os.mkdir(pdf_file_path_agent_name)
            pdf_file_path = os.path.join(assets_dir, "pdf", str(agent_id), pdf_file.filename)
            with open(pdf_file_path, "wb") as buffer:
                shutil.copyfileobj(pdf_file.file, buffer)
            pdf_file_url = "/" + pdf_file_path.replace("\\", "/")

    icon_file_url = None
    if icon_file is not None:
        if len(icon_file.filename) > 0:
            icon_file_path_agent_name = os.path.join(assets_dir, "avatar", str(agent_id))
            if not os.path.exists(icon_file_path_agent_name):
                os.mkdir(icon_file_path_agent_name)
            icon_file_path = os.path.join(assets_dir, "avatar", str(agent_id), icon_file.filename)
            with open(icon_file_path, "wb") as buffer:
                shutil.copyfileobj(icon_file.file, buffer)
            icon_file_url = "/" + icon_file_path.replace("\\", "/")

    voice_model_file_url = None
    if voice_model_file is not None:
        if len(voice_model_file.filename) > 0:
            voice_model_file_path_agent_name = os.path.join(assets_dir, "model", str(agent_id))
            if not os.path.exists(voice_model_file_path_agent_name):
                os.mkdir(voice_model_file_path_agent_name)
            voice_model_file_path = os.path.join(assets_dir, "model", str(agent_id), voice_model_file.filename)
            with open(voice_model_file_path, "wb") as buffer:
                shutil.copyfileobj(voice_model_file.file, buffer)
            voice_model_file_url = "/" + voice_model_file_path.replace("\\", "/")

    pinecone_namespace = str(user_id) + "_" + str(agent_id)

    ai_agent = AiAgent(
        id = agent_id,
        user_id = user_id,
        name = name,
        introduction = introduction,
        created_at = datetime.datetime.now(),
        pdf_file = pdf_file_url,
        icon_file = icon_file_url,
        voice_model_file = voice_model_file_url,
        pinecone_namespace = pinecone_namespace,
        age = age,
        first_person_pronoun = first_person_pronoun,
        second_person_pronoun = second_person_pronoun,
        activity = activity,
        hobbies = hobbies,
        occupation = occupation,
        speaking_style = speaking_style,
    )

    db.add(ai_agent)
    db.commit()
    db.refresh(ai_agent)

    agent_id = ai_agent.id

    if sample_dialogs:
        list_sample_dialog = json.loads(sample_dialogs)

        if list_sample_dialog:
            for sample_dialog in list_sample_dialog:
                db_sample_dialog = SampleDialog(
                    agent_id = agent_id,
                    content = sample_dialog["content"]
                )
                db.add(db_sample_dialog)
    
    if sample_voices:
        if len(sample_voices[0].filename) > 0:
            for sample_voice in sample_voices:
                sample_voice_url = None
                if sample_voice:
                    sample_voice_path_agent_name = os.path.join(assets_dir, "voice", str(agent_id))
                    if not os.path.exists(sample_voice_path_agent_name):
                        os.mkdir(sample_voice_path_agent_name)
                    sample_voice_path = os.path.join(assets_dir, "voice", str(agent_id), sample_voice.filename)
                    with open(sample_voice_path, "wb") as buffer:
                        shutil.copyfileobj(sample_voice.file, buffer)
                    sample_voice_url = "/" + sample_voice_path.replace("\\", "/")

                db_sample_voice = SampleVoice(
                    agent_id = agent_id,
                    file = sample_voice_url
                )
                db.add(db_sample_voice)
    
    db.commit()

    return ai_agent

# Update aiagent
@router.put("/aiagents/update/{aiagent_id}")
async def update_aiagent(
    aiagent_id: int,
    name: Optional[str] = Form(None),
    introduction: Optional[str] = Form(None),
    pdf_file: Optional[UploadFile] = File(None),
    icon_file: Optional[UploadFile] = File(None),
    voice_model_file: Optional[UploadFile] = File(None),
    pinecone_namespace: Optional[str] = Form(None),
    age: Optional[int] = Form(None),
    first_person_pronoun: Optional[str] = Form(None),
    second_person_pronoun: Optional[str] = Form(None),
    activity: Optional[str] = Form(None),
    hobbies: Optional[str] = Form(None),
    occupation: Optional[str] = Form(None),
    speaking_style: Optional[str] = Form(None),
    sample_dialogs: Optional[str] = Form(None),
    sample_voices_info: Optional[str] = Form(None),
    sample_voices_file: Optional[List[UploadFile]] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    ai_agent = db.query(AiAgent).filter(AiAgent.id == aiagent_id).first()
    user = db.query(User).filter(User.id == ai_agent.user_id).first()

    if user.name != current_user:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not ai_agent:
        raise HTTPException(status_code=404, detail="Ai agent not found")
    
    if name and name != ai_agent.name:
        ai_agent.name = name
    if introduction and introduction != ai_agent.introduction:
        ai_agent.introduction = introduction
    if pinecone_namespace and pinecone_namespace != ai_agent.pinecone_namespace:
        ai_agent.pinecone_namespace = pinecone_namespace
    if age and age != ai_agent.age:
        ai_agent.age = age
    if first_person_pronoun and first_person_pronoun != ai_agent.first_person_pronoun:
        ai_agent.first_person_pronoun = first_person_pronoun
    if second_person_pronoun and second_person_pronoun != ai_agent.second_person_pronoun:
        ai_agent.second_person_pronoun = second_person_pronoun
    if activity and activity != ai_agent.activity:
        ai_agent.activity = activity
    if hobbies and hobbies != ai_agent.hobbies:
        ai_agent.hobbies = hobbies
    if occupation and occupation != ai_agent.occupation:
        ai_agent.occupation = occupation
    if speaking_style and speaking_style != ai_agent.speaking_style:
        ai_agent.speaking_style = speaking_style
    
    pdf_file_url = None
    if pdf_file is not None:
        if len(pdf_file.filename) > 0:
            pdf_file_path_agent_name = os.path.join(assets_dir, "pdf", str(aiagent_id))
            if not os.path.exists(pdf_file_path_agent_name):
                os.mkdir(pdf_file_path_agent_name)
            pdf_file_path = os.path.join(assets_dir, "pdf", str(aiagent_id), pdf_file.filename)
            with open(pdf_file_path, "wb") as buffer:
                shutil.copyfileobj(pdf_file.file, buffer)
            pdf_file_url = "/" + pdf_file_path.replace("\\", "/")
            ai_agent.pdf_file = pdf_file_url

    icon_file_url = None
    if icon_file is not None:
        if len(icon_file.filename) > 0:
            icon_file_path_agent_name = os.path.join(assets_dir, "avatar", str(aiagent_id))
            if not os.path.exists(icon_file_path_agent_name):
                os.mkdir(icon_file_path_agent_name)
            icon_file_path = os.path.join("assets", "avatar", str(aiagent_id), icon_file.filename)
            with open(icon_file_path, "wb") as buffer:
                shutil.copyfileobj(icon_file.file, buffer)
            icon_file_url = "/" + icon_file_path.replace("\\", "/")
            ai_agent.icon_file = icon_file_url

    voice_model_file_url = None
    if voice_model_file is not None:
        if len(voice_model_file.filename) > 0:
            voice_model_file_path_agent_name = os.path.join(assets_dir, "model", str(aiagent_id))
            if not os.path.exists(voice_model_file_path_agent_name):
                os.mkdir(voice_model_file_path_agent_name)
            voice_model_file_path = os.path.join("assets", "model", str(aiagent_id), voice_model_file.filename)
            with open(voice_model_file_path, "wb") as buffer:
                shutil.copyfileobj(voice_model_file.file, buffer)
            voice_model_file_url = "/" + voice_model_file_path.replace("\\", "/")
            ai_agent.voice_model_file = voice_model_file_url

    db.merge(ai_agent)
    db.commit()
    db.refresh(ai_agent)

    aiagent_id = ai_agent.id

    if sample_dialogs:
        list_sample_dialog = json.loads(sample_dialogs)

        if list_sample_dialog:
            sample_dialosg_db = db.query(SampleDialog).filter(SampleDialog.agent_id == aiagent_id).offset(skip).limit(limit).all()
            for sample_dialog_db in sample_dialosg_db:
                result = list(filter(lambda x: x.get('id') == sample_dialog_db.id, list_sample_dialog))
                if len(result) == 0:
                    db.delete(sample_dialog_db)
                else:
                    sample_dialog_db.content = result[0]["content"]
                    db.merge(sample_dialog_db)
            for sample_dialog in list_sample_dialog:
                if sample_dialog.get("id") is None:
                    db_sample_dialog = SampleDialog(
                        agent_id = aiagent_id,
                        content = sample_dialog["content"]
                    )
                    db.add(db_sample_dialog)
    
    if sample_voices_file:
        if len(sample_voices_file[0].filename) > 0 and sample_voices_info:
            list_sample_voice_info = json.loads(sample_voices_info)
            for index, sample_voice_info in enumerate(list_sample_voice_info):
                if sample_voice_info["type"] == 'DELETE':
                    sample_delete = db.query(SampleVoice).filter(SampleVoice.id == sample_voice_info["id"]).first()
                    if not sample_delete:
                        raise HTTPException(status_code=404, detail="Sample dialog delete not found")
                    db.delete(sample_delete)
                    sample_voices_file.insert(index, None)
                if sample_voice_info["type"] == 'UPDATE':
                    sample_update = db.query(SampleVoice).filter(SampleVoice.id == sample_voice_info["id"]).first()
                    if not sample_update:
                        raise HTTPException(status_code=404, detail="Sample dialog update not found")
                    sample_voice_url = None
                    if sample_voices_file[index]:
                        sample_voice_path = os.path.join("assets", "voice", str(aiagent_id), sample_voices_file[index].filename)
                        with open(sample_voice_path, "wb") as buffer:
                            shutil.copyfileobj(sample_voices_file[index].file, buffer)
                        sample_voice_url = "/" + sample_voice_path.replace("\\", "/")
                    sample_update.file = sample_voice_url
                    db.merge(sample_update)
                if sample_voice_info["type"] == 'CREATE':
                    sample_voice_url = None
                    if sample_voices_file[index]:
                        sample_voice_path = os.path.join("assets", "voice", str(aiagent_id), sample_voices_file[index].filename)
                        with open(sample_voice_path, "wb") as buffer:
                            shutil.copyfileobj(sample_voices_file[index].file, buffer)
                        sample_voice_url = "/" + sample_voice_path.replace("\\", "/")

                    db_samplevoice = SampleVoice(
                        agent_id = aiagent_id,
                        file = sample_voice_url
                    )
                    db.add(db_samplevoice)

    db.commit()

    return ai_agent

# Delete aiagent by id
@router.delete("/aiagents/delete/{aiagent_id}")
async def delete_samplevoice(
    aiagent_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    ai_agent = db.query(AiAgent).filter(AiAgent.id == aiagent_id).first()
    user = db.query(User).filter(User.id == ai_agent.user_id).first()

    if user.name != current_user:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not ai_agent:
        raise HTTPException(status_code=404, detail="Ai agent not found")
    db.delete(ai_agent)
    db.commit()

    return {"result": "delete success"}