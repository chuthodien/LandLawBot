from db import *
from database.models import *

def get_agent_by_id(agent_id:int, db = SessionLocal()):
    agent = db.query(AiAgent).where(AiAgent.id == agent_id).first()
    return agent