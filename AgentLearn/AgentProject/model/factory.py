from abc import ABC, abstractmethod
from typing import Optional
from langchain.embeddings import Embeddings
from langchain.chat_models import BaseChatModel
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.chat_models.tongyi import ChatTongyi
from of_config_handler import rag_conf, agent_conf

class BaseModelFactory(ABC):
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        pass
    
class ChatModelFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings|BaseChatModel]:
        return ChatTongyi(model=agent_conf["chat_model_name"], api_key=agent_conf["api_key"])
        
class EmbeddingModelFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return DashScopeEmbeddings(model=agent_conf["embedding_model_name"], dashscope_api_key=agent_conf["DASHSCOPE_API_KEY"])
    
chat_model = ChatModelFactory().generator()
embed_model = EmbeddingModelFactory().generator()
