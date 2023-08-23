import logging
from typing import Callable, Optional
import typing

from fastapi import APIRouter, WebSocket
from vocode.streaming.agent.base_agent import BaseAgent
from AIME_deepgram.websocket import (
    AudioConfigStartMessage,
    AudioMessage,
    InputAudioConfig,
    OutputAudioConfig,
    ReadyMessage,
    WebSocketMessage,
    WebSocketMessageType,
)
from vocode.streaming.output_device.websocket_output_device import WebsocketOutputDevice
from AIME_streaming_conversation import AimeStreamingConversation
from vocode.streaming.synthesizer.base_synthesizer import BaseSynthesizer
from vocode.streaming.transcriber.base_transcriber import BaseTranscriber
from vocode.streaming.utils.base_router import BaseRouter
import requests
import os

from core.agent.aime_chat_agent import AimeChatAgent

INFERENCE_HOST = os.getenv('INFERENCE_HOST') or "127.0.0.1"
INFERENCE_PORT = os.getenv('INFERENCE_PORT') or 50011

class AIMEConversationRouter(BaseRouter):
    def __init__(
        self,
        transcriber_thunk: Callable[[InputAudioConfig], BaseTranscriber],
        agent: BaseAgent,
        synthesizer_thunk: Callable[[OutputAudioConfig], BaseSynthesizer],
        logger: Optional[logging.Logger] = None,
    ):
        super().__init__()
        self.transcriber_thunk = transcriber_thunk
        self.agent = agent
        self.synthesizer_thunk = synthesizer_thunk
        self.logger = logger or logging.getLogger(__name__)
        self.router = APIRouter()
        self.router.websocket("/conversation/{characterID}")(self.conversation)

    async def get_characterID(self, path):
        return path['characterID']
    
    def send_preload_model(self, characterID):
        requests.post("http://{}:{}/load_model?character_id={}".format(INFERENCE_HOST, INFERENCE_PORT, characterID))

    def send_del_model(self, characterID):
        requests.post("http://{}:{}/delete_model?character_id={}".format(INFERENCE_HOST, INFERENCE_PORT, characterID))

    def get_conversation(
        self,
        output_device: WebsocketOutputDevice,
        start_message: AudioConfigStartMessage,
        characterID: str,
    ) -> AimeStreamingConversation:
        transcriber = self.transcriber_thunk(start_message.input_audio_config)
        synthesizer = self.synthesizer_thunk(start_message.output_audio_config)
        synthesizer.synthesizer_config.should_encode_as_wav = True
        return AimeStreamingConversation(
            output_device=output_device,
            transcriber=transcriber,
            agent=self.agent,
            synthesizer=synthesizer,
            conversation_id=start_message.conversation_id,
            logger=self.logger,
            characterID=characterID
        )

    async def conversation(self, websocket: WebSocket):
        characterID = await self.get_characterID(websocket.path_params)
        self.agent.agent_config.characterID = characterID

        await self.agent.create_system_message()

        await websocket.accept()
        start_message: AudioConfigStartMessage = AudioConfigStartMessage.parse_obj(
            await websocket.receive_json()
        )
        self.logger.debug(f"Conversation started")
        output_device = WebsocketOutputDevice(
            websocket,
            start_message.output_audio_config.sampling_rate,
            start_message.output_audio_config.audio_encoding,
        )
        
        self.send_preload_model(characterID)
        conversation = self.get_conversation(output_device, start_message, characterID)
        await conversation.start(lambda: websocket.send_text(ReadyMessage().json()))
        while conversation.is_active():
            message: WebSocketMessage = WebSocketMessage.parse_obj(
                await websocket.receive_json()
            )
            if message.type == WebSocketMessageType.STOP:
                break
            audio_message = typing.cast(AudioMessage, message)
            conversation.receive_audio(audio_message.get_bytes())
        self.send_del_model(characterID)

        output_device.mark_closed()
        # del conversation.agent.memory
        conversation.terminate()

        
    def get_router(self) -> APIRouter:
        return self.router
