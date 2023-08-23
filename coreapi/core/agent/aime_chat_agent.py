import openai
import json
from typing import Generator, Optional, Tuple, AsyncGenerator
import logging

from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import ChatMessage, AIMessage
from langchain.prompts import (
    ChatPromptTemplate, 
    SystemMessagePromptTemplate, 
    MessagesPlaceholder, 
    HumanMessagePromptTemplate
)
from vocode import getenv
from vocode.streaming.agent.base_agent import BaseAgent

from core.agent.prompt import AI_RULE_PPROMPT
from core.models.agent import AimeChatAgentConfig

from core.agent.utils import stream_openai_response_async, get_agent_context

from vocode.streaming.agent.chat_agent import ChatAgent
from vocode.streaming.models.agent import ChatGPTAgentConfig

class AimeChatAgent(ChatAgent[AimeChatAgentConfig]):
    def __init__(
        self,
        agent_config: AimeChatAgentConfig,
        logger: logging.Logger = None,
        openai_api_key: Optional[str] = None,
    ):
        super().__init__(agent_config)
        openai.api_key = openai_api_key or getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY must be set in environment or passed in")
        self.agent_config = agent_config
        self.logger = logger or logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.context = get_agent_context(self.agent_config.characterID, self.agent_config.agent_language) if self.agent_config.characterID else ""
        self.prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(AI_RULE_PPROMPT.format(context=self.context, language=self.agent_config.agent_language)),
                MessagesPlaceholder(variable_name="history"),
                HumanMessagePromptTemplate.from_template("{input}"),
            ]
        )

        print(f"Prompt: {self.prompt}")

        if agent_config.initial_message:
            if (
                agent_config.generate_responses
            ):  # we use ChatMessages for memory when we generate responses
                self.memory.chat_memory.messages.append(
                    ChatMessage(
                        content=agent_config.initial_message.text, role="assistant"
                    )
                )
            else:
                self.memory.chat_memory.add_ai_message(
                    agent_config.initial_message.text
                )

        self.llm = ChatOpenAI(
            model_name=self.agent_config.model_name,
            temperature=self.agent_config.temperature,
            max_tokens=self.agent_config.max_tokens,
            openai_api_key=openai.api_key,
        )
        self.conversation = ConversationChain(
            memory=self.memory, prompt=self.prompt, llm=self.llm
        )
        self.first_response = (
            self.create_first_response(agent_config.expected_first_prompt)
            if agent_config.expected_first_prompt
            else None
        )
        self.is_first_response = True

    async def create_system_message(self):
        self.context = get_agent_context(self.agent_config.characterID, self.agent_config.agent_language)
        if not self.agent_config.generate_responses:
            self.prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessagePromptTemplate.from_template(AI_RULE_PPROMPT.format(context=self.context, language=self.agent_config.agent_language)),
                    MessagesPlaceholder(variable_name="history"),
                    HumanMessagePromptTemplate.from_template("{input}"),
                ]
            )
            self.conversation = ConversationChain(
                memory=self.memory, prompt=self.prompt, llm=self.llm
            )

    def create_first_response(self, first_prompt):
        return self.conversation.predict(input=first_prompt)

    async def respond(
        self,
        human_input,
        is_interrupt: bool = False,
        conversation_id: Optional[str] = None,
    ) -> Tuple[str, bool]:
        if is_interrupt and self.agent_config.cut_off_response:
            cut_off_response = self.get_cut_off_response()
            self.memory.chat_memory.add_user_message(human_input)
            self.memory.chat_memory.add_ai_message(cut_off_response)
            return cut_off_response, False
        self.logger.debug("LLM responding to human input")
        if self.is_first_response and self.first_response:
            self.logger.debug("First response is cached")
            self.is_first_response = False
            text = self.first_response
        else:
            text = await self.conversation.apredict(input=human_input)
        self.logger.debug(f"LLM response: {text}")
        return text, False

    async def generate_response(
        self,
        human_input: str,
        conversation_id: Optional[str] = None,
        is_interrupt: bool = False,
    ) -> AsyncGenerator[str, None]:
        self.memory.chat_memory.messages.append(
            ChatMessage(role="user", content=human_input)
        )
        if is_interrupt and self.agent_config.cut_off_response:
            cut_off_response = self.get_cut_off_response()
            self.memory.chat_memory.messages.append(
                ChatMessage(role="assistant", content=cut_off_response)
            )
            yield cut_off_response
            return
        prompt_messages = [
            ChatMessage(role="system", content=AI_RULE_PPROMPT.format(context=self.context, language=self.agent_config.agent_language))
        ] + self.memory.chat_memory.messages
        bot_memory_message = ChatMessage(role="assistant", content="")
        self.memory.chat_memory.messages.append(bot_memory_message)
        
        stream = await openai.ChatCompletion.acreate(
            model=self.agent_config.model_name,
            messages=[
                prompt_message.dict(include={"content": True, "role": True})
                for prompt_message in prompt_messages
            ],
            max_tokens=self.agent_config.max_tokens,
            temperature=self.agent_config.temperature,
            stream=True,
        )
        
        async for message in stream_openai_response_async(
            stream,
            get_text=lambda choice: choice.get("delta", {}).get("content"),
        ):
            bot_memory_message.content = f"{bot_memory_message.content} {message}"
            yield message

    def update_last_bot_message_on_cut_off(self, message: str):
        for memory_message in self.memory.chat_memory.messages[::-1]:
            if (
                isinstance(memory_message, ChatMessage)
                and memory_message.role == "assistant"
            ) or isinstance(memory_message, AIMessage):
                memory_message.content = message
                return
              
    def terminate(self):
        del self.memory
        self.memory = ConversationBufferMemory(return_messages=True)

if __name__ == "__main__":
    from vocode.streaming.models.message import BaseMessage
    import asyncio
    agent=AimeChatAgent(
        AimeChatAgentConfig(
            initial_message=BaseMessage(text="こんにちは"),
            prompt_preamble="",
            generate_responses=True,
            temperature=0,
            characterID=1,
            agent_language="Japanese"
        )
    )

    async def print_generated_response():
        while True:
            generator = agent.generate_response(human_input=input("Human: "), conversation_id="123")
            i = 0
            async for text in generator:
                print(f"num: {i} - generate: {text}")
                i += 1

    # Assuming your_object is an instance of the class containing the generate_response method
    asyncio.run(print_generated_response())
    agent.terminate()