import sys, importlib
from pathlib import Path
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.vectorstores import Pinecone
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings

from fastapi import Depends
from sqlalchemy.orm import Session
# from database.models import User, Sample_Dialog
# from database.connectDB import SessionLocal, engine

PARENT_DIR = "path\\to\\AIME"

def import_parents(level=1):
    global __package__
    file = Path(__file__).resolve()
    parent, top = file.parent, file.parents[level]
    
    sys.path.append(str(top))
    try:
        sys.path.remove(str(parent))
    except ValueError: # already removed
        pass

    __package__ = '.'.join(parent.parts[len(top.parts):])
    importlib.import_module(__package__)

if __name__ == "__main__" and __package__ is None:
    import_parents(level=2)

from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import Pinecone
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings

from fastapi import Depends
from sqlalchemy.orm import Session
from database.models import User, SampleDialog
from database.connectDB import SessionLocal, engine
from typing import List

PARENT_DIR = "path\\to\\AIME"

def create_index(index_name, namespace, doc_path):
    loader = TextLoader(doc_path, encoding='utf8')
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings()
    Pinecone.from_documents(docs, embeddings, index_name=index_name, namespace=namespace)

def get_content_dialogs_by_agent_id(db: Session, agents_id):
    return db.query(SampleDialog).filter(SampleDialog.agents_id == agents_id).all()
  
def create_index_from_dialog(index_name, namespace, chracter_id: int, db:Session):    
    dialogs: List[SampleDialog] = get_content_dialogs_by_agent_id(db, agents_id=chracter_id)
    documents = ""
    for dialog in dialogs:
        documents = documents + " " + dialog.content
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings()
    Pinecone.from_documents(docs, embeddings, index_name=index_name, namespace=namespace)
