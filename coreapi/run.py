import datetime
import os
import logging
import requests
from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError
import vocode
import json
import uvicorn
import shutil

from fastapi import Depends, FastAPI, Form, HTTPException, UploadFile, File, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
# from fastapi.openapi.utils import get_openapi
# from fastapi.staticfiles import StaticFiles
from fastapi_utils.tasks import repeat_every
from linebot.models import RichMenu, RichMenuSize, RichMenuArea, PostbackAction, RichMenuBounds, URIAction

from vocode import getenv
# from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.synthesizer import AzureSynthesizerConfig, GoogleSynthesizerConfig
# from vocode.streaming.agent.chat_gpt_agent import ChatGPTAgent
# from vocode.streaming.client_backend.conversation import ConversationRouter
from vocode.streaming.models.message import BaseMessage
from AIME_deepgram.transcriber import (
    PunctuationEndpointingConfig,
)

# from vocode.streaming.models.websocket import InputAudioConfig
# from vocode.streaming.transcriber.deepgram_transcriber import DeepgramTranscriber, DeepgramTranscriberConfig
# from vocode.streaming.synthesizer.azure_synthesizer import AzureSynthesizer
# from vocode.streaming.synthesizer.google_synthesizer import GoogleSynthesizer

# from langchain.document_loaders import TextLoader
# from langchain.embeddings.openai import OpenAIEmbeddings
# from langchain.text_splitter import CharacterTextSplitter
# from langchain.vectorstores import Chroma
# from langchain.document_loaders import TextLoader

from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler

# from AIME_google_synthesizer import GoogleSynthesizer
from AIME_azure_synthesizer import AzureSynthesizer
from AIME_conversation import AIMEConversationRouter
from AIME_deepgram_transcriber import DeepgramTranscriber, DeepgramTranscriberConfig

from core.agent.aime_chat_agent import AimeChatAgent
from core.models.agent import AimeChatAgentConfig
from core.memory.pinecone import create_index, PARENT_DIR
# from core.agent.utils import get_agent_context

from api.endpoints import router as api_router
from db import *
# from database.utils import get_agent_by_id

import argparse

from middleware.authentication import create_call_token

CALENDAR_CRON_JOB = 604800

load_dotenv()

line_channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN_LOGIN')
line_channel_secret = os.getenv('LINE_CHANNEL_SECRET_LOGIN')
login_redirect_uri = os.getenv('LOGIN_REDIRECT_URI')

LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
URL_CALL = os.getenv('URL_CALL')


def generate_app() -> FastAPI:
    #App config
    app = FastAPI()

    app.include_router(api_router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    language = os.getenv("LANGUAGE_DEEPGRAM")
    
    if language == "ja":
        model="general"
        voice_name="ja-JP-AoiNeural"
        agent_language="Japanese"
    elif language == "en":
        model="nova"
        voice_name="en-US-AriaNeural"
        agent_language="English"
    
    conversation_router = AIMEConversationRouter(
        transcriber_thunk=lambda input_audio_config: DeepgramTranscriber(
            DeepgramTranscriberConfig(
                sampling_rate=input_audio_config.sampling_rate,
                audio_encoding=input_audio_config.audio_encoding,
                chunk_size=input_audio_config.chunk_size,
                endpointing_config=PunctuationEndpointingConfig(),
                downsampling=input_audio_config.downsampling,
                is_safari=input_audio_config.is_safari,
                model=model,
                min_interrupt_confidence=0.3,
                # mute_during_speech=False,
                language=language
            )
        ),
        agent=AimeChatAgent(
            AimeChatAgentConfig(
                initial_message=BaseMessage(text="Hello!"),
                prompt_preamble=f"Have a pleasant conversation",
                generate_responses=True,
                agent_language=agent_language,
            )
        ),
        synthesizer_thunk=lambda output_audio_config: AzureSynthesizer(
            AzureSynthesizerConfig(
                voice_name=voice_name,
                sampling_rate=output_audio_config.sampling_rate,
                audio_encoding=output_audio_config.audio_encoding,
            )
        ),
        logger=logger,
    )
    
    app.include_router(conversation_router.get_router())

    @app.get("/docs", response_class=HTMLResponse)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url="openapi.json",
            title="AIME API Documentation",
            swagger_js_url="/static/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger-ui.css",
        )
      
    ## function for testing api document
    @app.get('/text_to_text')
    async def text_to_text():
        return {"message": ""}

    @app.post("/characters/{user_id}")
    async def create_character_memory(
        user_id : str,
        namespace : str,
        background_tasks: BackgroundTasks,
        index_name : str = 'characters',
        file: UploadFile = File(...),
    ):
        file_name = f"{PARENT_DIR}\\coreapi\\docs\\{user_id}_{namespace}.pdf"

        with open(file_name, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        background_tasks.add_task(create_index, index_name, namespace, file_name)
        return {"message": "Memory create in the background"}

    @app.on_event("startup")
    @repeat_every(seconds=CALENDAR_CRON_JOB)  # 7 day
    def cron_job_remove_update_line_id() -> None:
        db = SessionLocal()
        try:
            # get all rich_menu_id to delete with Line API
            query = db.query(User.rich_menu_id).all()
            rich_menu_ids = [result[0] for result in query]
            for rich_menu_id in rich_menu_ids:
                line_bot_api.delete_rich_menu(rich_menu_id)

            # update all field rich_menu_id in table User = None
            deleteRichMenus = update(User).values(rich_menu_id=None)
            db.execute(deleteRichMenus)
            db.commit()

            # get all line_id + create rich_menu + link rich_menu_id + line_id
            query = db.query(User.line_id).all()
            line_ids = [result[0] for result in query]

            for line_id in line_ids:
                token = create_call_token({"line_id": line_id})
                urlCall = str(URL_CALL) + str(token)
                rich_menu = RichMenu(
                        size=RichMenuSize(width=2500, height=1000), 
                        selected=True,
                        name='Call Agent',
                        chat_bar_text='Menu',
                        areas=[
                            RichMenuArea(
                                bounds=RichMenuBounds(x=0, y=0, width=2500, height=1000), 
                                action=URIAction(label='Option 1', uri=urlCall, text= "option1"),
                            )
                        ]
                    )
                
                rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu)

                # Upload rich menu image
                with open('img/iconCall.jpg', 'rb') as f:
                    line_bot_api.set_rich_menu_image(rich_menu_id, 'image/jpeg', f)
                line_bot_api.link_rich_menu_to_user(line_id, rich_menu_id)

                # Update rich_menu_id new for line_id
                stmt = update(User).where(User.line_id == line_id).values(rich_menu_id=rich_menu_id)
                db.execute(stmt)

            db.commit()
        except Exception as e:
            db.rollback()
        finally:
            db.close()

    return app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WebSocket Endpoint")
    parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="Hosting default: 0.0.0.0"
    )
    parser.add_argument(
        "--port", type=int, default=5000
    )

    args = parser.parse_args()

    uvicorn.run(
        generate_app(),
        host=args.host,
        port=args.port,
    )
    