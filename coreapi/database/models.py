from datetime import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Identity
from sqlalchemy.orm import relationship

from .connectDB import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True, index=True)
    name =  Column(String(255))
    email = Column(String(100))
    line_id = Column(String(255))
    created_at = Column(DateTime(), default=datetime.now())
    pinecone_index =  Column(String(255))
    access_token =  Column(String(1000))
    refresh_token =  Column(String(255))
    user_name =  Column(String(255))
    rich_menu_id =  Column(String(255))

    ai_agents = relationship("AiAgent", back_populates="user", cascade="all,delete")

    def __repr__(self):
        return f"{self.email}"
    
class AiAgent(Base):
    __tablename__ = "ai_agents"
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(255))
    introduction = Column(String(255))
    created_at = Column(DateTime(), default=datetime.now())
    pdf_file = Column(String(255))
    icon_file = Column(String(255))
    voice_model_file = Column(String(255))
    pinecone_namespace = Column(String(255))
    age = Column(Integer)
    first_person_pronoun = Column(String(255))
    second_person_pronoun = Column(String(255))
    activity = Column(String(255))
    hobbies = Column(String(255))
    occupation = Column(String(255))
    speaking_style = Column(String(255))

    user = relationship("User", back_populates="ai_agents")
    sample_voices = relationship("SampleVoice", back_populates="ai_agents", cascade="all,delete")
    sample_dialogs = relationship("SampleDialog", back_populates="ai_agents", cascade="all,delete")

    def __repr__(self):
        return f"{self.name}"

class SampleVoice(Base):
    __tablename__ = "sample_voices"
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("ai_agents.id", ondelete="CASCADE"))
    file = Column(String(255))

    ai_agents = relationship("AiAgent", back_populates="sample_voices")

class SampleDialog(Base):
    __tablename__ = "sample_dialogs"
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("ai_agents.id", ondelete="CASCADE"))
    content = Column(String(255))

    ai_agents = relationship("AiAgent", back_populates="sample_dialogs")