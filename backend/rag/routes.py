import logging
from fastapi import APIRouter, HTTPException
from rag.schemas import QueryRequest
from dependencies import get_rag_service
from settings import TOP_K_RESULTS

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/query")
async def query_rag(request: QueryRequest):
    """Test RAG retrieval without voice"""
    try:
        rag = get_rag_service()
        results = await rag.retrieve(request.query, top_k=TOP_K_RESULTS)
        return {
            "query": request.query,
            "results": results
        }
    except Exception as e:
        logger.error(f"Error querying RAG: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
