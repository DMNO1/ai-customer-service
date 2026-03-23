"""
Chat Schemas (Pydantic models)
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime

class MessageRequest(BaseModel):
    """Request model for sending a message"""
    agent_id: str = Field(..., description="Agent ID to send message to")
    message: str = Field(..., min_length=1, max_length=4000, description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    meta: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

    @validator('message')
    def message_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()

class MessageResponse(BaseModel):
    """Response model for chat message"""
    response: str = Field(..., description="AI response text")
    session_id: str = Field(..., description="Session ID")
    agent_id: str = Field(..., description="Agent that responded")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Confidence score")
    sources: Optional[List[Dict[str, Any]]] = Field(None, description="Source documents if RAG used")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional response metadata")
    created_at: Optional[datetime] = Field(None, description="Response timestamp")

class ConversationHistory(BaseModel):
    """Model for a single message in conversation history"""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")

class StreamChunk(BaseModel):
    """Model for streaming response chunk"""
    content: str = Field(..., description="Partial response content")
    done: bool = Field(False, description="Whether this is the final chunk")

class AgentInfo(BaseModel):
    """Agent information model"""
    agent_id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Agent display name")
    description: Optional[str] = Field(None, description="Agent description")
    llm_provider: str = Field("openai", description="LLM provider name")
    model_name: str = Field("gpt-3.5-turbo", description="Model to use")
    has_knowledge_base: bool = Field(False, description="Whether agent uses knowledge base")
    is_active: bool = Field(True, description="Whether agent is active")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")

class HealthStatus(BaseModel):
    """System health status"""
    status: str = Field(..., description="Overall status: 'healthy', 'degraded', 'unhealthy'")
    services: Dict[str, str] = Field(..., description="Individual service statuses")
    database: Dict[str, Any] = Field(..., description="Database status")
    uptime: float = Field(..., description="Uptime in seconds")
    version: str = Field(..., description="API version")

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")
