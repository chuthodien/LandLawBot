import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from run import app
from database.models import Base
from database.connectDB import get_db
from database import User, AiAgent, SampleDialog, SampleVoice
from middleware import create_access_token

SQLALCHEMY_DB_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DB_URL
)

TestingSessionLocal = sessionmaker()
TestingSessionLocal.configure(bind = engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

access_token = create_access_token({"user_name": "admin", "line_id": "123456", "line_access_token": "line_access_token"})

@pytest.fixture()
def make_user(
    name: str = "admin",
    email: str = "admin@example.com",
    line_id: str = "123456",
    pinecone_index: str = "index",
    access_token: str = access_token,
    refresh_token: str = "refresh_token"
):
    user = User(   
        name = name,
        email = email,
        line_id = line_id,
        pinecone_index = pinecone_index, 
        access_token = access_token,
        refresh_token = refresh_token
    )
    return user



@pytest.fixture()
def make_aiagent(
    user_id: int = 1,
    name: str = "Gon Freecss",
    introduction: str = "Hunter of the 287th generation. Enhancer-type Nen user. Birthday is May 5th. Height is 154cm. Weight is 49kg. Blood type is B.",
    pdf_file: str = "file.pdf",
    icon_file: str = None,
    voice_model_file: str = None,
    pinecone_namespace: str ="pinecone name",
    age: int = 15,
    first_person_pronoun: str = "I (ore)",
    second_person_pronoun: str = "you (kimi)",
    activity: str = "Taking the Hunter Exam",
    hobbies: str = "Fighting",
    occupation: str = "Hunter",
    speaking_style: str = "A quiet boy of around 12 years old"
):
    aiagent = AiAgent(
        user_id = user_id,
        name = name,
        introduction = introduction,
        pdf_file = pdf_file,
        icon_file = icon_file,
        voice_model_file = voice_model_file,
        pinecone_namespace = pinecone_namespace,
        age = age,
        first_person_pronoun = first_person_pronoun,
        second_person_pronoun = second_person_pronoun,
        activity = activity,
        hobbies = hobbies,
        occupation = occupation,
        speaking_style = speaking_style
    )
    return aiagent

@pytest.fixture()
def make_sampledialog(
    agent_id: int = 1,
    content: str = "Dialog1"
):  
    sampledialog = SampleDialog(
        agent_id = agent_id,
        content = content
    )
    return sampledialog

@pytest.fixture()
def make_samplevoice(
    agent_id: int = 1,
    file: str = "voice.wav"
):  
    samplevoice = SampleVoice(
        agent_id = agent_id,
        file = file
    )
    return samplevoice

@pytest.fixture(name="client")
def test_db(make_user, make_aiagent, make_sampledialog, make_samplevoice):
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    db = TestingSessionLocal()
    db.add(make_user)
    db.add(make_aiagent)
    db.add(make_sampledialog)
    db.add(make_samplevoice)
    db.commit()
    yield client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)



    
