"""
RAG (Retrieval-Augmented Generation) Pipeline
实现向量检索和问答逻辑。
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv
# 修复导入问题：使用新的langchain模块路径
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
# 修复导入问题：使用正确的langchain模块路径
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAI
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter

# 加载环境变量
load_dotenv()

class RAGPipeline:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        self.vector_store = self._init_vector_store()
        self.qa_chain = self._init_qa_chain()
    
    def _init_vector_store(self):
        """初始化向量数据库连接"""
        # 检查API密钥是否存在
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            # 如果没有设置Pinecone API密钥，则使用内存中的向量存储进行模拟
            print("Warning: PINECONE_API_KEY not set, using mock vector store for testing")
            return MockVectorStore()
        
        # 使用Pinecone类来初始化，然后传递给PineconeVectorStore
        pc = Pinecone(api_key=api_key)
        
        # 这里简化处理，实际项目中应包含错误处理和备选方案（如Milvus）
        return PineconeVectorStore(
            pinecone_api_key=api_key,
            index_name="ai-customer-service",
            embedding=self.embeddings
        )
    
    def _init_qa_chain(self):
        """初始化问答链"""
        llm = OpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))
        retriever = self.vector_store.as_retriever()
        
        # 构建提示模板
        template = """Use the following pieces of context to answer the question at the end. 
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Use three sentences maximum and keep the answer as concise as possible.
        {context}
        Question: {question}
        Helpful Answer:"""
        
        prompt = ChatPromptTemplate.from_template(template)
        
        # 构建RAG链
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
        )
        
        return chain
    
    def answer_question(self, query: str) -> Dict[str, Any]:
        """
        根据用户查询生成答案。
        
        Args:
            query: 用户的自然语言问题。
            
        Returns:
            包含答案和来源文档的字典。
        """
        try:
            result = self.qa_chain.invoke(query)
            return {
                "answer": result,
                "sources": []  # 在这个实现中，源文档没有直接返回，需要额外处理
            }
        except Exception as e:
            # 在实际应用中，这里会调用 error_handler.py 中的函数
            print(f"Error in RAG pipeline: {e}")
            return {
                "answer": "抱歉，我无法回答这个问题。请稍后再试。",
                "sources": []
            }

# 模拟向量存储类，用于测试
class MockVectorStore:
    def as_retriever(self):
        return MockRetriever()

class MockRetriever:
    def __init__(self):
        pass
    
    def __or__(self, func):
        # 返回一个mock函数，用于format_docs
        def mock_format_docs(query):
            # 返回一些模拟的文档内容
            return "This is mock context based on your query."
        return mock_format_docs

# 用于测试的主函数
if __name__ == "__main__":
    pipeline = RAGPipeline()
    test_query = "你们的产品有哪些功能？"
    answer = pipeline.answer_question(test_query)
    print(f"Q: {test_query}")
    print(f"A: {answer['answer']}")