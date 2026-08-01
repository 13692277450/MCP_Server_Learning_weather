import sys
import os

# 确保父目录 AgentProject/ 在 sys.path 中，以便从 rag/ 子目录也能导入同级模块
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PARENT_DIR = os.path.dirname(_CURRENT_DIR)
if _PARENT_DIR not in sys.path:
    sys.path.insert(0, _PARENT_DIR)

from langchain_chroma import Chroma
from of_config_handler import chroma_conf
from model.factory import embed_model
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from of_path_tool import get_abs_path
from of_file_handler import listdir_with_allowed_type, txt_loader, pdf_loader, get_file_md5_hex
from of_logger_handler import logger
from langchain_core.documents import Document



class VectorStoreService:
    def __init__(self):
        self.vector_store = Chroma(
            collection_name=chroma_conf['collection_name'],
            persist_directory=get_abs_path(chroma_conf['persist_directory']),
            embedding_function=embed_model, # type: ignore
            
        )
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_conf['chunk_size'],
            chunk_overlap=chroma_conf['chunk_overlap'],
            separators=chroma_conf['separators'],
            length_function=len,
        )
    def get_retriever(self):
        return self.vector_store.as_retriever(
            search_kwargs={"k": chroma_conf['k']},
        )
    def load_document(self):
        
        def check_md5_hex(md5_for_check:str):
            if not os.path.exists(get_abs_path(chroma_conf['md5_hex_store'])):
                open(get_abs_path(chroma_conf['md5_hex_store']), "w").close()
                return False
            with open(get_abs_path(chroma_conf['md5_hex_store']), "r") as f:
                for line in f.readlines():
                    line = line.strip()
                    if line == md5_for_check:
                        return True
                return False
        def save_md5_hex(md5_for_check:str):
            with open(get_abs_path(chroma_conf['md5_hex_store']), "a") as f:
                f.write(md5_for_check + "\n")
                # return True
                
        def get_file_document(read_path:str):
            if read_path.endswith("txt"):
                return txt_loader(read_path)
            elif read_path.endswith("pdf"):
                return pdf_loader(read_path)
            return []
        allowd_files_path = listdir_with_allowed_type(
            get_abs_path(chroma_conf['data_path']),
            tuple(chroma_conf['allowed_knowledge_file_types']),
        )
        for path in allowd_files_path:
            md5_hex = get_file_md5_hex(path)
            if check_md5_hex(md5_hex): # type: ignore
                logger.info(f"[加载知识库] {path} 已存在，跳过加载")
                continue
            try:
                documents: list[Document] = get_file_document(path)
                if not documents:
                    logger.error(f"[加载知识库] {path} 加载失败，文档为空")
                    continue
                split_documents: list[Document] = self.spliter.split_documents(documents)
                if not split_documents:
                    logger.error(f"[加载知识库] {path} 分块失败，没有有效文档")
                    continue
                self.vector_store.add_documents(split_documents)
                save_md5_hex(md5_hex) # type: ignore
                logger.info(f"[加载知识库] {path} 加载成功，文档数量：{len(split_documents)}")
            except Exception as e:
                logger.error(f"[加载知识库] {path} 加载失败，错误信息：{str(e)}", exc_info=True) # exc_info=True 打印完整错误信息
                continue
            
if __name__ == "__main__":
    vs = VectorStoreService()
    vs.load_document()
    retriever = vs.get_retriever()
    res = retriever.invoke("迷路")
    for r in res:
        print(r.page_content)
        print("="*50)