from vector_store import VectorStoreService
from of_prompt_loader import load_rag_prompts
from langchain_core.prompts import PromptTemplate
import os   
from model.factory import chat_model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

def print_prompt(prompt):
    print("="*50)
    print(prompt.to_string())
    print("="*50)
    return prompt

class RagSummarizedService(object):
    def __init__(self):
        self.vector_store=VectorStoreService()
        self.retriever = self.vector_store.get_retriever()
        self.prompt_text = load_rag_prompts()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.model = chat_model
        self.chain = self.__init_chain()
        
    def __init_chain(self):
        chain = self.prompt_template | print_prompt | self.model | StrOutputParser() # type: ignore
        return chain
    
    def retriever_docs(self, query: str)-> list[Document]:
        return self.retriever.invoke(query)
        
    def rag_summarize(self, query: str)-> str:
        context_docs = self.retriever_docs(query)
        context = ""
        counter =0
        for doc in context_docs:
            counter += 1
            context += f"[参考资料{counter}]:参考资料:{doc.page_content} |参考元数据: {doc.metadata}\n"
        return self.chain.invoke(
            {
                "context": context,
                "input": query,
            }
        )
        
        
if __name__ == "__main__":
    rag_service = RagSummarizedService()
    print(rag_service.rag_summarize("小户型使用哪种扫地机器人"))
        
