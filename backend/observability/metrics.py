"""
Central Prometheus metrics registry.
"""
from prometheus_client import Counter, Histogram


class Metrics:
    # HTTP request metrics (auto-collected by middleware)
    http_requests_total = Counter(
        "http_requests_total",
        "Total HTTP requests",
        ["method", "path", "status"],
    )
    http_request_duration_seconds = Histogram(
        "http_request_duration_seconds",
        "HTTP request latency in seconds",
        ["method", "path"],
        buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
    )

    # Document upload metrics
    document_uploads_total = Counter(
        "document_uploads_total",
        "Total document uploads",
        ["status"],
    )
    document_processing_seconds = Histogram(
        "document_processing_seconds",
        "Document processing time in seconds",
        buckets=[0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
    )

    # RAG query metrics
    rag_queries_total = Counter(
        "rag_queries_total",
        "Total RAG queries",
        ["status"],
    )
    rag_query_duration_seconds = Histogram(
        "rag_query_duration_seconds",
        "RAG query latency in seconds",
        buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
    )
    rag_results_count = Histogram(
        "rag_results_count",
        "Number of results returned per RAG query",
        buckets=[0, 1, 2, 3, 5, 10],
    )

    # Voice pipeline metrics
    voice_rag_injections_total = Counter(
        "voice_rag_injections_total",
        "Total RAG context injections in voice pipeline",
        ["status"],
    )


metrics = Metrics()
