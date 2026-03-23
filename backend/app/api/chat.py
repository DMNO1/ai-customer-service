"""
对话 (Chat) API 路由
"""

import asyncio
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from typing import Optional, List
import json

from app.api.schemas import ChatRequest, ChatResponse, ChatMessage
from app.services.chat_service import chat_service
from app.core.exceptions import LLMException, VectorStoreException, NotFoundException
import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/chat", tags=["chat"])

# 内存存储对话历史（生产环境使用数据库/Redis）
_conversations = {}

@router.post("/completions", response_model=ChatResponse)
async def chat_completion(req: ChatRequest):
    """
    智能对话接口

    基于知识库向量检索 + LLM 生成回答
    """
    try:
        # 对话ID用于追踪
        conversation_id = str(uuid.uuid4())

        # 获取历史
        history = req.history
        if req.conversation_id:
            conversation_id = req.conversation_id
            history = _conversations.get(conversation_id, [])

        # 执行对话
        result = await chat_service.chat(
            knowledge_base_id=req.knowledge_base_id,
            query=req.message,
            provider=req.provider,
            temperature=req.temperature,
            stream=False,
            history=history
        )

        # 保存到历史
        _conversations[conversation_id] = history + [
            {"role": "user", "content": req.message},
            {"role": "assistant", "content": result["answer"]}
        ]

        # 限制历史长度
        if len(_conversations[conversation_id]) > 40:
            _conversations[conversation_id] = _conversations[conversation_id][-40:]

        # 异步发送飞书通知（非阻塞）
        try:
            # 异步任务应该交给 Celery，这里简单 fire-and-forget
            asyncio.create_task(
                chat_service.notify_feishu_new_chat(
                    user_id="unknown",  # TODO: 从 request.state.user 获取
                    knowledge_base_name="",  # TODO: 查询知识库名称
                    query=req.message,
                    answer_preview=result["answer"][:100]
                )
            )
        except:
            pass

        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            provider=result["provider"],
            tokens_used=result.get("tokens_used"),
            conversation_id=conversation_id
        )

    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except (LLMException, VectorStoreException) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)
    except Exception as e:
        logger.error("chat_endpoint_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="对话服务暂时不可用"
        )

@router.post("/completions/stream")
async def chat_completion_stream(req: ChatRequest):
    """
    流式对话接口 - SSE 响应
    """
    async def generate():
        try:
            # 简化版流式，未使用 conversation history
            async for chunk in chat_service.chat(
                knowledge_base_id=req.knowledge_base_id,
                query=req.message,
                provider=req.provider,
                temperature=req.temperature,
                stream=True,
                history=req.history
            ):
                yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"

            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error("stream_chat_error", error=str(e))
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """删除对话历史"""
    if conversation_id in _conversations:
        del _conversations[conversation_id]
        return {"success": True}
    raise HTTPException(status_code=404, detail="对话不存在")

@router.get("/conversations")
async def list_conversations(limit: int = 100):
    """列��最近对话（仅ID）"""
    return {
        "conversation_ids": list(_conversations.keys())[:limit],
        "total": len(_conversations)
    }
