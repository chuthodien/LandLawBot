import datetime
import os

from pydantic import BaseModel
from core.agent.aime_chat_agent import AimeChatAgent
from core.models.agent import AimeChatAgentConfig
from vocode.streaming.models.message import BaseMessage
from core.agent.utils import get_vectorstore
from vocode import getenv
from fastapi import APIRouter, HTTPException, Request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FollowEvent, RichMenu, RichMenuSize, RichMenuArea, PostbackAction, RichMenuBounds, URIAction
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
import shutil
from database import User, get_db, SessionLocal, AiAgent
import json
import requests
import asyncio
import tracemalloc

from middleware.authentication import create_call_token, decode_access_token

router = APIRouter()

index_name = "characters"
namespace = "doctor"

vectorstore = get_vectorstore(
    api_key= getenv("PINECONE_API_KEY"),
    environment= getenv("PINECONE_ENVIRONMENT"),
    index="characters",
    character="hienjp",
)

URL_CALL = os.getenv('URL_CALL')

retriever=vectorstore.as_retriever(search_kwargs={"k": 1})

LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

agent=AimeChatAgent(
        AimeChatAgentConfig(
            initial_message=BaseMessage(text="Hello"),
            prompt_preamble="",
            generate_responses=False,
            temperature=0,
            index_name="aichat",
            namespace="ai-rule",
            characterID=2,
            agent_language="Vietnamese"
        )
    )

# Test Webhook
@router.get("/webhook/test")
async def verify_webhook():
    return {"AIME": "AIME test"}

@router.get("/webhook/verifyTokenToCall/{token}")
async def verify_token_to_call(token: str):
    if not token:
        raise  HTTPException(status_code=404, detail="Token not found")
    payload = decode_access_token(token)
    exp = payload.get("exp")
    exp_time = datetime.datetime.utcfromtimestamp(exp)
    now = datetime.datetime.utcnow()
    if now >= exp_time:
        raise HTTPException(status_code=403, detail="Token expired")
    else:
        return { "verifyTokenToCall": True }
    
# Event flow bot
@handler.add(FollowEvent)
def handle_follow(event: FollowEvent):
    reply_text_welcome = "Cảm ơn bạn đã đến với AIME ☺️! Tôi nên gọi bạn là gì?"
    db = SessionLocal()
    try:
        line_id = event.source.user_id
        user = db.query(User).filter(User.line_id == line_id).first()

        if not user:
            # init rich menu
            rich_menu = RichMenu(
                size=RichMenuSize(width=2500, height=1000), 
                selected=False,
                name='Call Agent',
                chat_bar_text='Menu',
                areas=[
                    RichMenuArea(
                        bounds=RichMenuBounds(x=0, y=0, width=2500, height=1000),
                        action=PostbackAction(label='Option 1', data='option1')
                    )
                ]
            )

            rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu)
            # Upload rich menu image
            with open('img/iconCall.jpg', 'rb') as f:
                line_bot_api.set_rich_menu_image(rich_menu_id, 'image/jpeg', f)

            line_bot_api.link_rich_menu_to_user(line_id, rich_menu_id)

            newUser = User(
                    name = 'name' + '_' + str(line_id),
                    line_id = line_id,
                    created_at = datetime.datetime.now(),
                    pinecone_index = "pinecone_index",
                    access_token = '',
                    refresh_token = '',
                )
            db.add(newUser)
            db.commit()
            db.refresh(newUser)

            # send message welcome !!!
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text_welcome))
        else:
            line_bot_api.link_rich_menu_to_user(line_id, user.refresh_token)
            # send message welcome !!!
            if not user.user_name:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text_welcome))
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Xin chào!"))

# # Event chat
@handler.add(MessageEvent, message = TextMessage)
def handle_message(event: MessageEvent):

    line_id = event.source.user_id
    if isinstance(event, MessageEvent):
        db = SessionLocal()
        line_id = event.source.user_id
        user = db.query(User).filter(User.line_id == line_id).first()

        # message first
        if not user.user_name:
            user.user_name = event.message.text
            db.merge(user)
            db.commit()
            db.refresh(user)
            
            reply_message_user_name = 'Cảm ơn bạn đã trò chuyện😊 : ' + event.message.text  + '. Đừng quên gọi cho tôi! Bạn cũng có thể gọi cho tôi từ menu bên dưới!'+ '. Tôi ở đây để trả lời cho bạn. Bạn có những câu hỏi nào? '
            line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text = reply_message_user_name),
                )

        else:
            # chatGpt response
            tracemalloc.start()
            async def generated_response_from_chat_gpt():
                response = await agent.respond(human_input=event.message.text)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text = response[0]),
                )
            asyncio.create_task(generated_response_from_chat_gpt())
            agent.terminate()
            # async def generated_response_from_chat_gpt():
            #     response =  agent.generate_response(human_input=event.message.text)
            #     async for text in response:
            #         line_bot_api.reply_message(
            #             event.reply_token,
            #             TextSendMessage(text),
            #         )
            # asyncio.create_task(generated_response_from_chat_gpt())
            # agent.terminate()
        
        if not user.rich_menu_id:
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

            user.rich_menu_id = rich_menu_id
            db.merge(user)
            db.commit()
            db.refresh(user)

# start
@router.post('/webhook/chat')
async def line_chat(request: Request):
    signature = request.headers['X-Line-Signature']
    body = await request.body()
    try:
        handler.handle(body.decode('utf-8'), signature)
    except InvalidSignatureError:
        return "Invalid signature"
    
    return {"messenger": body.decode('utf-8')}