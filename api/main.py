"""
API Routes for AI Customer Service System
FastAPI endpoints for the various services
"""

from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import uuid
from pathlib import Path

# Import our services
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.vector_store_service import VectorStoreService
from services.document_parser import DocumentParser
from services.web_scraper import WebScraper
from services.llm_provider import LLMProviderFactory

# Initialize services
vector_store = VectorStoreService()
document_parser = DocumentParser()
web_scraper = WebScraper()
llm_factory = LLMProviderFactory()

# Initialize FastAPI app
app = FastAPI(title="AI Customer Service API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class KnowledgeBaseSearchRequest(BaseModel):
    knowledge_base_id: str
    query: str
    k: Optional[int] = 5

class KnowledgeBaseSearchResponse(BaseModel):
    results: List[Dict[str, Any]]

class AddUrlRequest(BaseModel):
    knowledge_base_id: str
    url: str

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    messages: List[ChatMessage]
    provider: str = "openai"
    model: Optional[str] = None
    temperature: Optional[float] = 0.7

class ChatCompletionResponse(BaseModel):
    response: str

@app.post("/knowledge/bases/{knowledge_base_id}/search", response_model=KnowledgeBaseSearchResponse)
async def search_knowledge_base(request: KnowledgeBaseSearchRequest):
    """Search in a specific knowledge base using vector similarity"""
    try:
        results = vector_store.similarity_search(
            knowledge_base_id=request.knowledge_base_id,
            query=request.query,
            k=request.k)
        return KnowledgeBaseSearchResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching knowledge base: {str(e)}")

@app.post("/knowledge/bases/{knowledge_base_id}/documents")
async def add_document_to_knowledge_base(knowledge_base_id: str, file: UploadFile = File(...)):
    """Upload and add a document to a knowledge base"""
    try:
        # Create temporary file
        temp_dir = Path("./temp_uploads")
        temp_dir.mkdir(exist_ok=True)
        
        file_path = temp_dir / f"{uuid.uuid4()}_{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Add document to vector store
        success = vector_store.add_document(knowledge_base_id, str(file_path))
        
        # Clean up temp file
        os.remove(file_path)
        
        if success:
            return {"message": "Document added successfully", "filename": file.filename}
        else:
            raise HTTPException(status_code=500, detail="Failed to add document to knowledge base")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding document: {str(e)}")

@app.post("/knowledge/bases/{knowledge_base_id}/add-url")
async def add_url_to_knowledge_base(request: AddUrlRequest):
    """Add content from a URL to a knowledge base"""
    try:
        # Scrape content from URL
        content = web_scraper.scrape_url(request.url)
        if not content:
            raise HTTPException(status_code=400, detail="Failed to scrape URL content")
        
        # Save content temporarily
        temp_dir = Path("./temp_uploads")
        temp_dir.mkdir(exist_ok=True)
        
        temp_filename = f"{uuid.uuid4()}_url_content.txt"
        file_path = temp_dir / temp_filename
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Add to vector store
        success = vector_store.add_document(request.knowledge_base_id, str(file_path))
        
        # Clean up temp file
        os.remove(file_path)
        
        if success:
            return {"message": "URL content added successfully", "url": request.url}
        else:
            raise HTTPException(status_code=500, detail="Failed to add URL content to knowledge base")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding URL content: {str(e)}")

@app.post("/chat/completion", response_model=ChatCompletionResponse)
async def chat_completion(request: ChatCompletionRequest):
    """Generate chat completion using specified LLM provider"""
    try:
        # Convert Pydantic messages to dict format
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Create provider instance
        provider = llm_factory.create_provider(
            request.provider,
            model=request.model
        )
        
        # Generate response
        response = provider.chat_completion(
            messages=messages,
            model=request.model,
            temperature=request.temperature
        )
        
        return ChatCompletionResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating chat completion: {str(e)}")

@app.get("/providers")
async def list_providers():
    """List available LLM providers"""
    return {"providers": llm_factory.list_available_providers()}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Customer Service API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)