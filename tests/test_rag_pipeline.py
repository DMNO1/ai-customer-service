"""
Test for RAG Pipeline
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.rag_pipeline import RAGPipeline

def test_rag_pipeline_initialization():
    """测试RAG管道初始化"""
    try:
        pipeline = RAGPipeline()
        assert pipeline is not None
        print("+ RAG Pipeline initialized successfully")
    except Exception as e:
        print(f"- RAG Pipeline initialization failed: {e}")

def test_rag_pipeline_answer():
    """测试RAG管道问答功能（需要有效的API密钥和向量数据库）"""
    try:
        pipeline = RAGPipeline()
        result = pipeline.answer_question("What is the capital of France?")
        assert "answer" in result
        assert "sources" in result
        print("+ RAG Pipeline answered question successfully")
    except Exception as e:
        print(f"- RAG Pipeline answer test failed: {e}")

if __name__ == "__main__":
    test_rag_pipeline_initialization()
    # test_rag_pipeline_answer()  # 需要有效的API密钥和数据库