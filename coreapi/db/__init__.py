import os
from dotenv import load_dotenv
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = automap_base()
Base.prepare(autoload_with=engine)
User = Base.classes.users
AiAgents = Base.classes.ai_agents
SampleVoices = Base.classes.sample_voices
SampleDialogs = Base.classes.sample_dialogs

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()