from fastapi import FastAPI, HTTPException
from webapi.data_management import get_data, get_recommendations
from webapi.embeddings_processing import PipelineProcessor

__EMBEDDINGS_PMANAGER__ = PipelineProcessor()
app = FastAPI()


@app.get("/embeddings/status/jobs")
async def get_embeddings_jobs_status():
    return __EMBEDDINGS_PMANAGER__.get_jobs_list()

@app.get("/embeddings/status/{job_id}")
async def get_embeddings_job_status(job_id: str):
    if not __EMBEDDINGS_PMANAGER__.has_job(job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    return __EMBEDDINGS_PMANAGER__.get_status(job_id)


@app.post("/embeddings/start", status_code=201)
async def start_embeddings_processing():
    if __EMBEDDINGS_PMANAGER__.is_running():
        raise HTTPException(
            status_code=409,  # HTTP 409: Conflict.
            detail={
                "message": "Cannot start embeddings processing, there is a previous job in progress",
                "status": __EMBEDDINGS_PMANAGER__.get_current_status()
            }
        )

    if __EMBEDDINGS_PMANAGER__.start():
        return __EMBEDDINGS_PMANAGER__.get_current_status()

    raise HTTPException(
        status_code=500,  # HTTP 500: Server Error.
        detail={
            "message": "Failed to start embeddings processing. Check spark status.",
            "status": __EMBEDDINGS_PMANAGER__.get_current_status()
        }
    )


@app.get("/data/search/{query_str}")
async def search_fulltext_query(query_str: str) -> list:
    return get_data(query_str).to_dict(orient="records")


@app.get("/data/recommendations/{sku}")
async def search_recommendations_sku(sku: str) -> list:
    return get_recommendations(sku).to_dict(orient="records")
