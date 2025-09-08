import logging
from contextlib import asynccontextmanager
from typing import Any
from fastapi import FastAPI, HTTPException, Request
from webapi.data_management import get_data, get_recommendations
from webapi.embeddings_processing import EmbeddingsPipelineProcessor

# -----------------------------
# App Lifecycle Setup
# -----------------------------

@asynccontextmanager
async def lifespan(api_app: FastAPI):
    # Startup: initialize the pipeline manager
    api_app.state.processor = EmbeddingsPipelineProcessor()
    try:
        yield
    except Exception as e:
        logging.exception(e)

    # Shutdown: release the lock before shutting down the api.
    api_app.state.processor.release()
    api_app.state.processor = None

def get_processor(rq: Request) -> EmbeddingsPipelineProcessor:
    return rq.app.state.processor
app = FastAPI(lifespan=lifespan)

# -----------------------------
# Api Endpoints
# -----------------------------

@app.post(
    path="/embeddings/start",
    status_code=201,
    summary="Starts an embeddings calculation pipeline job",
)
async def start_embeddings_processing(rq: Request) -> dict[str, Any]:
    processor = get_processor(rq)
    if processor.is_running():
        raise HTTPException(
            status_code=409,  # HTTP 409: Conflict.
            detail={
                "message": "Cannot start embeddings processing, there is a previous job in progress",
                "status": processor.get_current_status()
            }
        )

    if not processor.start():
        raise HTTPException(
            status_code=500,  # HTTP 500: Server Error.
            detail={
                "message": "Failed to start embeddings processing. Check spark status.",
                "status": processor.get_current_status()
            }
        )

    return processor.get_current_status()


@app.post(
    path="/embeddings/reindex",
    summary="Reindex search indexes in embeddings collection"
)
async def reindex_embeddings_indexes(rq: Request) -> list[dict[str, Any]]:
    return get_processor(rq).reindex().to_dict(orient="records")


@app.get(
    path="/embeddings/status/jobs",
    summary="Get status of all embeddings calculation jobs",
)
async def get_embeddings_jobs_status(rq: Request) -> list[dict[str, Any]]:
    return get_processor(rq).get_jobs_list()

@app.get(
    path="/embeddings/status/{job_id}",
    summary="Get status of a given embeddings calculation job",
)
async def get_embeddings_job_status(job_id: str, rq: Request) -> dict[str, Any]:
    processor = get_processor(rq)
    if not job_id or job_id.isspace():
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Job was not provided.",
                "status": 400
            }
        )
    elif not processor.has_job(job_id):
        raise HTTPException(
            status_code=404,
            detail={
                "message": f"Job {job_id} not found.",
                "status": 404
            }
        )
    return processor.get_status(job_id)


@app.get(
    path="/data/search/{query}",
    summary="Search for products by a given query using a full-text search index",
)
async def search_fulltext_query(query: str) -> list[dict[str, Any]]:
    if not query or query.isspace():
        raise HTTPException(
            status_code=400,
            detail={
                "message": "No query string provided.",
                "status": 400
            }
        )
    return get_data(query).to_dict(orient="records")


@app.get(
    path="/data/recommendations/{sku}",
    summary="Get recommendations for a given sku using similarity vectors"
)
async def search_recommendations_sku(sku: str) -> list[dict[str, Any]]:
    if not sku or sku.isspace():
        raise HTTPException(
            status_code=400,
            detail={
                "message": "No sku provided.",
                "status": 400
            }
        )
    return get_recommendations(sku).to_dict(orient="records")
