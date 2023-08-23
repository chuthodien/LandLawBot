import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from langchain.vectorstores.pinecone import Pinecone
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.base import VectorStore
from typing import AsyncGenerator, AsyncIterable, Callable, Generator, Iterable, List
from openai.openai_object import OpenAIObject
import pinecone

SENTENCE_ENDINGS = [".", "!", "?", "！", "。", "？"]
#SENTENCE_ENDINGS = [".", "!", "?", "！", "。", "？", "、"]
from database.utils import get_agent_by_id

CONTEXT_TITLE = {
    "Vietnamese": [
        "Tên", 
        "Giới thiệu", 
        "Tuổi", 
        "Ngôi thứ nhất", 
        "Ngôi thứ hai", 
        "Hoạt động hiện tại",
        "Sở thích",
        "Nghề nghiệp",
        "Phong cách ngôn ngữ",
        "Đối thoại mẫu",
    ], 
    "English": [
        "Name", 
        "Introduction", 
        "Age",
        "First-person pronoun", 
        "Second-person pronoun", 
        "Current activity", 
        "Hobbies", 
        "Occupation", 
        "Speaking style", 
        "Sample dialogue",
    ]
}

def get_vectorstore(api_key:str, environment:str, index:str, character:str) -> VectorStore:
    pinecone.init(
        api_key=api_key,
        environment=environment
    )
    embedding_models = OpenAIEmbeddings()
    vector = Pinecone.from_existing_index(index_name=index, embedding=embedding_models, text_key="text", namespace=character)
    return vector

def format_dialogs(dialogs):
    result ="\"" + "\" \"".join(dialog.content for dialog in dialogs) + "\""
    return result

def get_agent_context(characterID, language):
    try:
        agent = get_agent_by_id(characterID)
        dialogs = format_dialogs(agent.sample_dialogs)

        context = f"""
            {CONTEXT_TITLE[language][0]}: {agent.name}
            {CONTEXT_TITLE[language][1]}: {agent.introduction}
            {CONTEXT_TITLE[language][2]}: {agent.age}
            {CONTEXT_TITLE[language][3]}: {agent.first_person_pronoun}
            {CONTEXT_TITLE[language][4]}: {agent.second_person_pronoun}
            {CONTEXT_TITLE[language][5]}: {agent.activity}
            {CONTEXT_TITLE[language][6]}: {agent.hobbies}
            {CONTEXT_TITLE[language][7]}: {agent.occupation}
            {CONTEXT_TITLE[language][8]}: {agent.speaking_style}
            {CONTEXT_TITLE[language][9]}: {dialogs}
        """

        print(f"Receive context: {context}")

        return context
    except: 
        return ""

def stream_llm_response(
    gen, get_text=lambda choice: choice['answer'], sentence_endings=SENTENCE_ENDINGS
) -> Generator:
    buffer = ""
    for response in gen:
        token = get_text(response)
        if not token:
            continue
        buffer += token
        if any(token.endswith(ending) for ending in sentence_endings):
            yield buffer.strip()
            buffer = ""
    if buffer.strip():
        yield buffer

async def stream_openai_response_async(
    gen: AsyncIterable[OpenAIObject],
    get_text: Callable[[dict], str],
    sentence_endings: List[str] = SENTENCE_ENDINGS,
) -> AsyncGenerator:
    buffer = ""
    async for event in gen:
        choices = event.get("choices", [])
        if len(choices) == 0:
            break
        choice = choices[0]
        if choice.finish_reason:
            break
        token = get_text(choice)
        if not token:
            continue
        buffer += token
        if any(token.endswith(ending) for ending in sentence_endings):
            yield buffer.strip()
            buffer = ""
    if buffer.strip():
        yield buffer

async def stream_openai_response_async(
    gen: AsyncIterable[OpenAIObject],
    get_text: Callable[[dict], str],
    sentence_endings: List[str] = SENTENCE_ENDINGS,
) -> AsyncGenerator:
    buffer = ""
    max_length = 20
    async for event in gen:
        choices = event.get("choices", [])
        if len(choices) == 0:
            break
        choice = choices[0]
        if choice.finish_reason:
            break
        token = get_text(choice)
        if not token:
            continue
        buffer += token
        if any(token.endswith(ending) for ending in sentence_endings):
            yield buffer.strip()
            buffer = ""
        # if (any(token.endswith(ending) for ending in sentence_endings) and len(buffer) > 1) or len(buffer) >= max_length:
        #     yield buffer.strip()
            buffer = ""
    if buffer.strip():
        yield buffer
