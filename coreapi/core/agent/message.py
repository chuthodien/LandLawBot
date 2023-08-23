import random
import time
from langchain.prompts.prompt import PromptTemplate
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate
)
from langchain.chains import ConversationChain
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAIChat
from langchain.memory import ConversationBufferMemory
from langchain.schema import ChatMessage, AIMessage
import openai
import json
from typing import Generator, Optional, Tuple

from typing import Generator
import logging
from vocode import getenv

from vocode.streaming.agent.base_agent import BaseAgent
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.message import BaseMessage
from langchain.vectorstores.base import VectorStore
from langchain.chains import ChatVectorDBChain
from langchain.callbacks.base import AsyncCallbackManager
from langchain.callbacks.tracers import LangChainTracer
from langchain.chains.chat_vector_db.prompts import (CONDENSE_QUESTION_PROMPT,
                                                     QA_PROMPT)
from langchain.chains.llm import LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.vectorstores.pinecone import Pinecone
import pinecone
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import LLMChain
from langchain.chains.question_answering import load_qa_chain
from typing import List
from langchain.schema import get_buffer_string
from langchain.callbacks.base import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

import sys
from typing import Any, Dict, List, Union

from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish, LLMResult
from langchain.document_loaders import DirectoryLoader, PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, TextSplitter

from prompt import AI_RULE_PPROMPT, ai_rule_template

SENTENCE_ENDINGS = [".", "!", "?"]


def create_index(index_name, namespace):
    pinecone.init(api_key=getenv("PINECONE_API_KEY"), environment=getenv("PINECONE_ENVIRONMENT"))
    index = pinecone.Index(index_name=index_name)
    loader = DirectoryLoader("D:\\Nam_4\\Thuc-tap-NCC\\Chatbot-AIME\\AIME\coreapi\\docs", loader_cls=PyMuPDFLoader)
    embeddings = OpenAIEmbeddings(openai_api_key=getenv("OPENAI_API_KEY"))
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)

    #Create and save vector embeddings to the Pinecone namespace
    vectorstore = Pinecone(index, embeddings.embed_query, text_key="text", namespace=namespace)
    vectorstore.add_documents(docs)
    

 
def get_vectorstore(api_key:str, environment:str, index:str, character:str) -> VectorStore:
    pinecone.init(
        api_key=api_key,
        environment=environment
    )
    embedding_models = OpenAIEmbeddings()
    vector = Pinecone.from_existing_index(index_name=index, embedding=embedding_models, text_key="text", namespace=character)
    return vector

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

class AimeChatAgentConfig(ChatGPTAgentConfig):
    index: str
    character: str

class AimeStreamingCallbackHandler(BaseCallbackHandler):
    """Callback handler for streaming. Only works with LLMs that support streaming."""

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Run when LLM starts running."""

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""


    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when LLM ends running."""

    def on_llm_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Run when LLM errors."""

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Run when chain starts running."""

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Run when chain ends running."""

    def on_chain_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Run when chain errors."""

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> None:
        """Run when tool starts running."""

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """Run on agent action."""
        pass

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Run when tool ends running."""

    def on_tool_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Run when tool errors."""

    def on_text(self, text: str, **kwargs: Any) -> None:
        """Run on arbitrary text."""

    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        """Run on agent end."""


class AimeChatAgent(BaseAgent):
    def __init__(
        self,
        agent_config: AimeChatAgentConfig,
        logger: logging.Logger = None,
        openai_api_key: Optional[str] = None,
        pinecone_api_key: Optional[str] = None,
        pinecone_environment: Optional[str] = None
    ):
        super().__init__(agent_config)
        openai.api_key = openai_api_key or getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY must be set in environment or passed in")
        self.agent_config = agent_config
        self.logger = logger or logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(self.agent_config.prompt_preamble),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessagePromptTemplate.from_template("{question}"),
            ]
        )
        self.memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history", input_key="question", ai_prefix="Character")
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
        if(self.agent_config.generate_responses):
            self.llm = ChatOpenAI(
                model_name=self.agent_config.model_name,
                temperature=self.agent_config.temperature,
                max_tokens=self.agent_config.max_tokens,
                openai_api_key=openai.api_key,
                streaming=True,
                callback_manager=CallbackManager([AimeStreamingCallbackHandler()]),
                verbose=True
            )
        else:
            self.llm =  ChatOpenAI(
                model_name=self.agent_config.model_name,
                temperature=self.agent_config.temperature,
                max_tokens=self.agent_config.max_tokens,
                openai_api_key=openai.api_key,
            )

        question_generator = LLMChain(llm=self.llm, prompt=AI_RULE_PPROMPT)
        doc_chain = load_qa_chain(self.llm, chain_type="map_reduce", )

        vectorstore = get_vectorstore(
            api_key=pinecone_api_key or getenv("PINECONE_API_KEY"),
            environment=pinecone_environment or getenv("PINECONE_ENVIRONMENT"),
            index=self.agent_config.index,
            character=self.agent_config.character,
        )

        # print(vectorstore)
        self.conversation = ConversationalRetrievalChain(question_generator=question_generator, combine_docs_chain=doc_chain, memory=self.memory, retriever=vectorstore.as_retriever(), get_chat_history=get_buffer_string)

        self.first_response = (
            self.create_first_response(agent_config.expected_first_prompt)
            if agent_config.expected_first_prompt
            else None
        )
        self.is_first_response = True

    def create_first_response(self, first_prompt):
        self.logger.debug("Create first response")
        text = self.conversation({"question": first_prompt, "chat_history":self.memory.buffer})
        return text["answer"]

    def respond(
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
            text = self.conversation({"question": human_input, "chat_history":self.memory.buffer})
        self.logger.debug(f"LLM response: {text['answer']}")
        return text['answer'], False

    def generate_response(
        self,
        human_input,
        is_interrupt: bool = False,
        conversation_id: Optional[str] = None,
    ) -> Generator[str, None, None]:
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
        
        messages = self.conversation({"question":human_input, "chat_history": self.memory.buffer})['answer']
        bot_memory_message = ChatMessage(role="assistant", content="")
        self.memory.chat_memory.messages.append(bot_memory_message)

        for message in stream_llm_response(
            map(lambda event: event, messages),
            get_text=lambda choice: choice,
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

if __name__ == "__main__":
    from dotenv import load_dotenv
    import vocode
    vocode.setenv(
        OPENAI_API_KEY="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",
        DEEPGRAM_API_KEY="85a559ba92007d708ab2d2b12c2f2e50f2c339fa",
        AZURE_SPEECH_KEY="b745886603bc4eee8b22022dfa694147",
        AZURE_SPEECH_REGION="eastus",
        PINECONE_API_KEY="32d7fb6b-c975-467a-bd40-40c6a28be846",
        PINECONE_ENVIRONMENT="us-west1-gcp-free"
    )
    index_name = "aichat"
    namespace = "ai-rule" 

    #create_index(index_name,namespace)

    load_dotenv()

    agent=AimeChatAgent(
        AimeChatAgentConfig(
            initial_message=BaseMessage(text="xin chao!"),
            prompt_preamble="Have a friendly conversation",
            index=index_name,
            character=namespace,
            temperature=1
        )
    )

    while True:
        # response = agent.respond(input("Human: "))[0]
        # print(f"AI: {response}")
        res = agent.respond(input("Human: "))
        print(f"AI: {res[0]}")