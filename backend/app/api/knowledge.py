"""
知识库 API 路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List, Optional
import uuid

from app.api.schemas import (
    KnowledgeBaseCreate,
    KnowledgeBaseResponse,
    DocumentUploadResponse,
    SearchRequest,
    SearchResult
)
from app.services.vector_store import vector_store
from app.services.document_parser import DocumentParser
from app.services.web_scraper import WebScraper
from app.core.exceptions import ValidationException, NotFoundException, DocumentParseException
import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/knowledge", tags=["knowledge"])

# 内存存储知识库元数据（生产环境应该用数据库）
_knowledge_bases = {}

@router.post("/bases", response_model=KnowledgeBaseResponse)
async def create_knowledge_base(data: KnowledgeBaseCreate):
    """创建知识库"""
    kb_id = str(uuid.uuid4())
    now = datetime.utcnow()

    _knowledge_bases[kb_id] = {
        "id": kb_id,
        "name": data.name,
        "description": data.description,
        "created_at": now,
        "updated_at": now,
        "document_count": 0
    }

    logger.info("knowledge_base_created", id=kb_id, name=data.name)
    return _knowledge_bases[kb_id]

@router.get("/bases", response_model=List[KnowledgeBaseResponse])
async def list_knowledge_bases():
    """列��所有知识库"""
    return list(_knowledge_bases.values())

@router.get("/bases/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(kb_id: str):
    """获取知识库详情"""
    kb = _knowledge_bases.get(kb_id)
    if not kb:
        raise NotFoundException("KnowledgeBase", kb_id)
    return kb

@router.post("/bases/{kb_id}/upload", response_model=DocumentUploadResponse)
async def upload_document(
    kb_id: str,
    file: UploadFile = File(...),
    chunk_size: int = Form(default=1000)
):
    """
    上传文档到知识库

    支持的格式: PDF, DOCX, PPTX, TXT, MD
    """
    # 验证知识库存在
    if kb_id not in _knowledge_bases:
        raise NotFoundException("KnowledgeBase", kb_id)

    # 保存临时文件
    temp_dir = Path("./tmp/uploads")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / f"{uuid.uuid4()}_{file.filename}"

    try:
        # 写入临时文件
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)

        # 解析文档
        logger.info("parsing_document", file=file.filename)
        text, file_type = DocumentParser.parse_file(str(temp_path))

        # 创建 Document 对象
        from langchain.docstore.document import Document
        doc = Document(
            page_content=text,
            metadata={
                "source": file.filename,
                "file_type": file_type,
                "size": len(content)
            }
        )

        # 添加到向量库
        from app.services.vector_store import vector_store
        added = vector_store.add_documents(kb_id, [doc])

        # 更新知识库统计
        _knowledge_bases[kb_id]["document_count"] += added
        _knowledge_bases[kb_id]["updated_at"] = datetime.utcnow()

        logger.info("document_uploaded", kb_id=kb_id, file=file.filename, chunks=added)

        return DocumentUploadResponse(
            id=str(uuid.uuid4()),
            filename=file.filename,
            file_type=file_type,
            status="completed",
            message=f"成功解析并添加 {added} 个文本片段",
            created_at=datetime.utcnow()
        )

    except DocumentParseException as e:
        logger.error("document_parse_failed", file=file.filename, error=e.message)
        return DocumentUploadResponse(
            id=str(uuid.uuid4()),
            filename=file.filename,
            file_type="unknown",
            status="failed",
            message=e.message,
            created_at=datetime.utcnow()
        )

    except Exception as e:
        logger.error("upload_failed", file=file.filename, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文档上传失败: {str(e)}"
        )

    finally:
        # 清理临时文件
        try:
            if temp_path.exists():
                temp_path.unlink()
        except:
            pass

@router.post("/bases/{kb_id}/add-url")
async def add_url_to_knowledge_base(
    kb_id: str,
    url: str = Form(..., description="网页URL"),
    parse_full_page: bool = Form(default=False, description="是否提取全页面HTML")
):
    """添加网页内容到知识库"""
    if kb_id not in _knowledge_bases:
        raise NotFoundException("KnowledgeBase", kb_id)

    try:
        from app.services.web_scraper import WebScraper

        async with WebScraper(use_playwright=True) as scraper:
            result = await scraper.scrape_url(url)

        # 创建 Document
        from langchain.docstore.document import Document
        doc = Document(
            page_content=result["text"][:10000],  # 限制长度
            metadata={
                "source": url,
                "title": result["title"],
                "method": result["method"]
            }
        )

        # 添加到向量库
        added = vector_store.add_documents(kb_id, [doc])
        _knowledge_bases[kb_id]["document_count"] += added
        _knowledge_bases[kb_id]["updated_at"] = datetime.utcnow()

        logger.info("url_added", kb_id=kb_id, url=url, chunks=added)

        return {
            "success": True,
            "url": url,
            "title": result["title"],
            "chunks_added": added,
            "content_length": len(result["text"])
        }

    except Exception as e:
        logger.error("add_url_failed", kb_id=kb_id, url=url, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"网页添加失败: {str(e)}"
        )

@router.post("/bases/{kb_id}/search", response_model=List[SearchResult])
async def search_knowledge_base(kb_id: str, req: SearchRequest):
    """向量检索"""
    if kb_id not in _knowledge_bases:
        raise NotFoundException("KnowledgeBase", kb_id)

    try:
        results = vector_store.similarity_search(
            knowledge_base_id=kb_id,
            query=req.query,
            top_k=req.top_k,
            score_threshold=req.score_threshold
        )

        logger.info("search_completed", kb_id=kb_id, count=len(results))
        return [SearchResult(**r) for r in results]

    except Exception as e:
        logger.error("search_failed", kb_id=kb_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"检索失败: {str(e)}"
        )

@router.delete("/bases/{kb_id}")
async def delete_knowledge_base(kb_id: str):
    """删除知识库及其所有向量"""
    if kb_id not in _knowledge_bases:
        raise NotFoundException("KnowledgeBase", kb_id)

    try:
        # 删除向量数据
        vector_store.delete_by_knowledge_base(kb_id)

        # 删除元数据
        del _knowledge_bases[kb_id]

        logger.info("knowledge_base_deleted", kb_id=kb_id)
        return {"success": True, "message": "知识库已删除"}

    except Exception as e:
        logger.error("delete_kb_failed", kb_id=kb_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除失败: {str(e)}"
        )
