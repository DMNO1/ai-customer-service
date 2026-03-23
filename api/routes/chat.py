"""
Chat API Routes
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid

from ..main import get_llm_factory, get_vector_store, get_agent_manager

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    agent_id: str
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = []
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    agent_id: str
    confidence: Optional[float] = None
    sources: Optional[List[Dict[str, Any]]] = None

@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint
    """
    try:
        agent_manager = get_agent_manager()
        llm_factory = get_llm_factory()
        vector_store = get_vector_store()

        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Retrieve agent configuration
        agent_config = agent_manager.get_agent_config(request.agent_id)
        if not agent_config:
            raise HTTPException(status_code=404, detail=f"Agent {request.agent_id} not found")

        # Build context from knowledge base if needed
        context = ""
        if agent_config.get("use_knowledge_base"):
            kb_id = agent_config.get("knowledge_base_id")
            if kb_id:
                search_results = vector_store.similarity_search(
                    knowledge_base_id=kb_id,
                    query=request.message,
                    k=5
                )
                if search_results:
                    context = "\n".join([r["content"] for r in search_results])

        # Build messages for LLM
        system_prompt = agent_config.get("system_prompt", "You are a helpful AI assistant.")
        if context:
            system_prompt += f"\n\nUse the following context to answer the user's question:\n{context}"

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(request.conversation_history)
        messages.append({"role": "user", "content": request.message})

        # Get response from LLM
        provider_name = agent_config.get("llm_provider", "openai")
        provider = llm_factory.create_provider(provider_name)
        response = provider.chat_completion(messages)

        return ChatResponse(
            response=response,
            session_id=session_id,
            agent_id=request.agent_id,
            confidence=0.9,  # Placeholder
            sources=[{"content": r["content"], "metadata": r["metadata"]} for r in search_results] if context else None
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
