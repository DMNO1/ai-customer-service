"""
向量存储服务 - RAG 检索核心
支持 ChromaDB(v1.0 API) 和 Milvus
"""

import os
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings.base import Embeddings
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document

from app.core.config import settings
from app.core.exceptions import VectorStoreException
import structlog

logger = structlog.get_logger()

class CustomOpenAIEmbeddings(Embeddings):
    """自定义 OpenAI 嵌入，支持异常重试"""

    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.model = model
        self.embedding = OpenAIEmbeddings(
            openai_api_key=api_key,
            model=model
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        try:
            return self.embedding.embed_documents(texts)
        except Exception as e:
            logger.error("embed_documents_failed", error=str(e))
            raise VectorStoreException(f"文档向量化失败: {str(e)}")

    def embed_query(self, text: str) -> List[float]:
        try:
            return self.embedding.embed_query(text)
        except Exception as e:
            logger.error("embed_query_failed", error=str(e))
            raise VectorStoreException(f"查询向量化失败: {str(e)}")


class VectorStoreService:
    """向量数据库服务 - 统一抽象层"""

    def __init__(self):
        self.db_type = settings.vector_db.lower()
        self.embeddings = CustomOpenAIEmbeddings(api_key=settings.openai_api_key)
        self._client = None
        self._init_client()

    def _init_client(self):
        """初始化向量数据库客户端"""
        try:
            if self.db_type == "chroma":
                self._init_chroma()
            elif self.db_type == "milvus":
                self._init_milvus()
            else:
                raise VectorStoreException(f"不支持的向量数据库类型: {self.db_type}")
        except Exception as e:
            logger.error("vector_store_init_failed", error=str(e))
            raise VectorStoreException(f"向量数据库初始化失败: {str(e)}")

    def _init_chroma(self):
        """初始化 ChromaDB 客户端（新版API）"""
        persist_dir = Path(settings.chroma_persist_dir)
        persist_dir.mkdir(parents=True, exist_ok=True)

        # 使用新版 Chroma 客户端
        self._client = chromadb.Client(ChromaSettings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=settings.chroma_persist_dir,
            anonymized_telemetry=False
        ))

        # 获取或创建集合
        try:
            self._collection = self._client.get_or_create_collection("knowledge_base")
            logger.info("chroma_client_initialized", count=self._collection.count())
        except Exception as e:
            logger.error("chroma_init_error", error=str(e))
            raise

    def _init_milvus(self):
        """初始化 Milvus 连接"""
        connections.connect(
            alias="default",
            host=settings.milvus_host,
            port=settings.milvus_port
        )

        # 检查集合是否存在，不存在则创建
        collection_name = "knowledge_base"
        if not utility.has_collection(collection_name):
            self._create_milvus_collection(collection_name)

        self._collection = Collection(collection_name)
        self._collection.load()
        logger.info("milvus_client_initialized")

    def _create_milvus_collection(self, name: str):
        """创建 Milvus 集合"""
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=100, is_primary=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=4000)
        ]
        schema = CollectionSchema(fields, description="RAG Knowledge Base")
        collection = Collection(name=name, schema=schema)

        # 创建索引
        index_params = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }
        collection.create_index(field_name="embedding", index_params=index_params)
        logger.info("milvus_collection_created", name=name)

    def add_documents(
        self,
        knowledge_base_id: str,
        documents: List[Document],
        batch_size: int = 100
    ) -> int:
        """
        添加文档到向量库

        Args:
            knowledge_base_id: 知识库ID
            documents: 文档列表

        Returns:
            int: 添加的文档数量
        """
        if not documents:
            return 0

        try:
            # 文本分割
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            splits = text_splitter.split_documents(documents)

            # 生成ID和元数据
            ids = []
            texts = []
            metadatas = []

            for i, doc in enumerate(splits):
                doc_id = str(uuid.uuid4())
                ids.append(doc_id)
                texts.append(doc.page_content)
                metadata = dict(doc.metadata) if doc.metadata else {}
                metadata["knowledge_base_id"] = knowledge_base_id
                metadata["doc_id"] = doc_id
                metadatas.append(metadata)

            # 向量化
            logger.info("generating_embeddings", count=len(texts))
            embeddings = self.embeddings.embed_documents(texts)

            # 写入向量库
            if self.db_type == "chroma":
                self._collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    documents=texts,
                    metadatas=metadatas
                )
            elif self.db_type == "milvus":
                data = [
                    ids,
                    embeddings,
                    texts,
                    [json.dumps(m, ensure_ascii=False) for m in metadatas]
                ]
                self._collection.insert(data)

            logger.info("documents_added", kb_id=knowledge_base_id, count=len(splits))
            return len(splits)

        except Exception as e:
            logger.error("add_documents_failed", kb_id=knowledge_base_id, error=str(e))
            raise VectorStoreException(f"添加文档失败: {str(e)}", operation="add_documents")

    def similarity_search(
        self,
        knowledge_base_id: str,
        query: str,
        top_k: int = 5,
        score_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        相似度搜索

        Args:
            knowledge_base_id: 知识库ID（过滤条件）
            query: 查询文本
            top_k: 返回结果数量
            score_threshold: 相似度阈值（ Chroma 0-1，Milvus 距离阈值）

        Returns:
            List of results with keys: text, metadata, score/distance
        """
        try:
            # 向量化查询
            query_embedding = self.embeddings.embed_query(query)

            if self.db_type == "chroma":
                # Chroma 使用新版查询 API
                where = {"knowledge_base_id": knowledge_base_id}
                results = self._collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where=where,
                    include=["documents", "metadatas", "distances"]
                )

                formatted = []
                for i in range(len(results["documents"][0])):
                    formatted.append({
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "score": 1 - results["distances"][0][i]  # 距离转相似度
                    })

                # 过滤阈值
                if score_threshold is not None:
                    formatted = [r for r in formatted if r["score"] >= score_threshold]

                return formatted

            elif self.db_type == "milvus":
                # Milvus 搜索
                search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
                results = self._collection.search(
                    data=[query_embedding],
                    anns_field="embedding",
                    param=search_params,
                    limit=top_k,
                    expr=f"knowledge_base_id == '{knowledge_base_id}'",
                    output_fields=["text", "metadata"]
                )

                formatted = []
                for hits in results:
                    for hit in hits:
                        formatted.append({
                            "text": hit.entity.get("text"),
                            "metadata": json.loads(hit.entity.get("metadata", "{}")),
                            "distance": hit.score  # L2 距离，越小越相似
                        })

                return formatted

        except Exception as e:
            logger.error("similarity_search_failed", kb_id=knowledge_base_id, error=str(e))
            raise VectorStoreException(f"向量搜索失败: {str(e)}", operation="similarity_search")

    def delete_by_knowledge_base(self, knowledge_base_id: str):
        """删除指定知识库的所有向量"""
        try:
            if self.db_type == "chroma":
                # Chroma 需要遍历删除
                results = self._collection.get(
                    where={"knowledge_base_id": knowledge_base_id},
                    include=["metadatas"]
                )
                if results["ids"]:
                    self._collection.delete(ids=results["ids"])
                    logger.info("chroma_documents_deleted", kb_id=knowledge_base_id, count=len(results["ids"]))

            elif self.db_type == "milvus":
                # Milvus 使用删除表达式
                expr = f"knowledge_base_id == '{knowledge_base_id}'"
                self._collection.delete(expr)
                logger.info("milvus_documents_deleted", kb_id=knowledge_base_id)

        except Exception as e:
            logger.error("delete_failed", kb_id=knowledge_base_id, error=str(e))
            raise VectorStoreException(f"删除向量失败: {str(e)}", operation="delete")

    def get_collection_stats(self) -> Dict[str, Any]:
        """获取向量库统计信息"""
        try:
            if self.db_type == "chroma":
                count = self._collection.count()
                return {"type": "chroma", "document_count": count}
            elif self.db_type == "milvus":
                count = self._collection.num_entities
                return {"type": "milvus", "document_count": count}
        except Exception as e:
            logger.error("get_stats_failed", error=str(e))
            return {"type": self.db_type, "error": str(e)}


# 全局向量存储服务实例
vector_store = VectorStoreService()
