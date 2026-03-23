"""
Knowledge Base API Routes
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os
import uuid
from pathlib import Path

from ..main import get_vector_store, get_document_parser
from ...services.document_parser import DocumentParser

router = APIRouter(prefix="/kb", tags=["knowledge-base"])

class KnowledgeBaseCreate(BaseModel):
    name: str
    description: Optional[str] = None
    agent_id: str

class KnowledgeBaseResponse(BaseModel):
    kb_id: str
    name: str
    description: Optional[str]
    document_count: int
    created_at: str

class DocumentAddRequest(BaseModel):
    kb_id: str
    content: Optional[str] = None
    url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

@router.post("/create", response_model=KnowledgeBaseResponse)
async def create_knowledge_base(request: KnowledgeBaseCreate):
    """Create a new knowledge base"""
    try:
        vector_store = get_vector_store()
        kb_id = f"kb_{uuid.uuid4().hex[:8]}"

        # In a full implementation, you'd save metadata to database
        # For now, we just return success
        return KnowledgeBaseResponse(
            kb_id=kb_id,
            name=request.name,
            description=request.description,
            document_count=0,
            created_at=uuid.UUID(hex=kb_id[3:]).time_last
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/document/add")
async def add_document(
    request: DocumentAddRequest,
    background_tasks: BackgroundTasks
):
    """Add a document to knowledge base"""
    try:
        vector_store = get_vector_store()
        parser = DocumentParser()

        # If content is provided directly
        if request.content:
            # For now, we'll create a temporary file
            temp_file = Path(f"temp_{uuid.uuid4().hex}.txt")
            temp_file.write_text(request.content, encoding='utf-8')
            success = vector_store.add_document(request.kb_id, str(temp_file))
            temp_file.unlink()
            
            if not success:
                raise HTTPException(status_code=500, detail="Failed to add document to vector store")
            
            return {"status": "success", "document_id": str(uuid.uuid4())}

        # If URL is provided (web scraping)
        if request.url:
            # This would integrate with WebScraper service
            # For now, return not implemented
            raise HTTPException(status_code=501, detail="URL ingestion not yet implemented")

        raise HTTPException(status_code=400, detail="Either content or url must be provided")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{kb_id}/search")
async def search_knowledge_base(kb_id: str, query: str, k: int = 5):
    """Search in knowledge base"""
    try:
        vector_store = get_vector_store()
        results = vector_store.similarity_search(kb_id, query, k)
        return {"kb_id": kb_id, "query": query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{kb_id}")
async def delete_knowledge_base(kb_id: str):
    """Delete a knowledge base and all its documents"""
    try:
        vector_store = get_vector_store()
        success = vector_store.delete_knowledge_base(kb_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete knowledge base")
        return {"status": "success", "message": f"Knowledge base {kb_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{kb_id}/stats")
async def get_kb_stats(kb_id: str):
    """Get knowledge base statistics"""
    try:
        vector_store = get_vector_store()
        # This would require implementing a count method in VectorStoreService
        # For now return placeholder
        return {
            "kb_id": kb_id,
            "document_count": 0,
            "total_chunks": 0,
            "last_updated": None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
