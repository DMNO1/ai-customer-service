"""
智能对话服务 - RAG + LLM 集成
构建完整的客服问答流程
"""

from typing import List, Dict, Any, Optional
import uuid

from app.services.vector_store import vector_store
from app.services.llm_service import llm_service
from app.services.document_parser import DocumentParser
from app.core.feishu_service import feishu_service
from app.core.exceptions import LLMException, VectorStoreException, AppException
import structlog

logger = structlog.get_logger()

class ChatService:
    """客服对话服务"""

    def __init__(self):
        self.vector_store = vector_store
        self.llm = llm_service
        self.feishu = feishu_service

    async def chat(
        self,
        knowledge_base_id: str,
        query: str,
        provider: Optional[str] = None,
        temperature: float = 0.7,
        stream: bool = False,
        history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        智能对话主入口

        Args:
            knowledge_base_id: 知识库ID
            query: 用户问题
            provider: LLM 提供者
            temperature: 温度参数
            stream: 是否流式返回
            history: 对话 histor message list

        Returns:
            Dict with answer, sources, tokens_used
        """
        try:
            1. 向量检索获取相关文档
            logger.info("searching_vector_store", kb_id=knowledge_base_id, query=query)
            search_results = self.vector_store.similarity_search(
                knowledge_base_id=knowledge_base_id,
                query=query,
                top_k=5,
                score_threshold=0.6
            )

            # 提取上下文
            context = self._build_context(search_results)

            2. 构建 prompt
            messages = self._build_messages(query, context, history)

            # 3. 调用 LLM
            if stream:
                # 流式返回
                return self._stream_response(messages, provider, temperature, search_results)
            else:
                # 非流式
                response = await self.llm.chat_completion(
                    messages=messages,
                    provider=provider,
                    temperature=temperature
                )
                return {
                    "answer": response,
                    "sources": self._format_sources(search_results),
                    "tokens_used": None,  # TODO: 从响应中提取
                    "provider": provider or self.llm.default_provider
                }

        except VectorStoreException as e:
            logger.error("vector_store_error", error=e.message)
            raise
        except LLMException as e:
            logger("llm_error", error=e.message)
            raise
        except Exception as e:
            logger.error("chat_failed", error=str(e))
            raise AppException(f"对话服务失败: {str(e)}")

    def _build_context(self, search_results: List[Dict[str, Any]]) -> str:
        """构建 RAG 上下文"""
        if not search_results:
            return "知识库中暂无相关文档。"

        context_parts = []
        for i, result in enumerate(search_results, 1):
            text = result["text"][:2000]  # 限制长度
            context_parts.append(f"[文档{i}] (相似度: {result.get('score', 0):.2f})\n{text}")

        return "\n\n".join(context_parts)

    def _build_messages(
        self,
        query: str,
        context: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """构建发送给 LLM 的消息列表"""
        system_prompt = """你是一个专业的客服助手。请根据提供的知识库文档回答用户问题。

知识库文档：
{context}

要求：
1. 只基于提供的文档回答，如果文档中没有答案，明确告知
2. 回答要简洁、专业、准确
3. 如果可能，引用具体的文档编号
4. 不要编造信息
5. 用中文回答""".format(context=context)

        messages = [{"role": "system", "content": system_prompt}]

        if history:
            # 添加最近 5 轮对话历史
            recent_history = history[-10:]  # 限制历史长度
            messages.extend(recent_history)

        messages.append({"role": "user", "content": query})
        return messages

    async def _stream_response(
        self,
        messages: List[Dict[str, str]],
        provider: Optional[str],
        temperature: float,
        search_results: List[Dict[str, Any]]
    ) -> AsyncGenerator[str, None]:
        """流式生成响应"""
        try:
            async for chunk in self.llm.chat_completion_stream(
                messages=messages,
                provider=provider,
                temperature=temperature
            ):
                yield chunk

        except Exception as e:
            logger.error("stream_response_failed", error=str(e))
            raise

    def _format_sources(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """格式化来源信息"""
        sources = []
        for r in search_results:
            meta = r.get("metadata", {})
            sources.append({
                "text": r["text"][:200] + "...",
                "score": r.get("score") or r.get("distance"),
                "knowledge_base_id": meta.get("knowledge_base_id"),
                "document_name": meta.get("source", "未知")
            })
        return sources

    async def notify_feishu_new_chat(
        self,
        user_id: str,
        knowledge_base_name: str,
        query: str,
        answer_preview: str
    ):
        """通知飞书新对话"""
        try:
            content = (
                f"用户ID: {user_id}\n"
                f"知识库: {knowledge_base_name}\n"
                f"问题: {query}\n"
                f"回答预览: {answer_preview[:100]}..."
            )
            await self.feishu.send_text(
                content=content,
                title="新客服对话"
            )
        except Exception as e:
            logger.warning("feishu_notification_failed", error=str(e))


# 全局对话服务
chat_service = ChatService()
