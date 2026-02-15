import time
import logging
from fastapi import APIRouter, HTTPException
from rag.schemas import QueryRequest
from dependencies import get_rag_service
from settings import TOP_K_RESULTS
from observability.metrics import metrics

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/query")
async def query_rag(request: QueryRequest):
    """Test RAG retrieval without voice"""
    try:
        rag = get_rag_service()
        start = time.perf_counter()
        results = await rag.retrieve(request.query, top_k=TOP_K_RESULTS)
        metrics.rag_query_duration_seconds.observe(time.perf_counter() - start)
        metrics.rag_results_count.observe(len(results))
        metrics.rag_queries_total.labels(status="success").inc()
        return {
            "query": request.query,
            "results": results
        }
    except Exception as e:
        metrics.rag_queries_total.labels(status="error").inc()
        logger.error(f"Error querying RAG: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
