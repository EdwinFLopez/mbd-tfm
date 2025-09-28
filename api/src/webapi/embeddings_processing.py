import threading
import uuid
from enum import Enum
from threading import Thread
from typing import Dict, Optional, List, Any
from webapi.data_management import (
    reindex_search_indexes, list_search_indexes
)


class EmbeddingsPipelineStatus(str, Enum):
    """Enumeration of possible statuses of the embeddings processing job."""
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class EmbeddingsPipelineProcessor:
    """
    Helper class to manage embeddings processing job status.
    Thread-safe implementation with error tracking.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._current_job: str = str(uuid.uuid4())
        self._errors: Dict[str, Optional[str]] = {
            self._current_job: None
        }
        self._processes: Dict[str, EmbeddingsPipelineStatus] = {
            self._current_job: EmbeddingsPipelineStatus.READY
        }

    # ---------------- Status helpers ---------------- #
    def release(self) -> None:
        if self._lock.acquire():
            self._lock.release()

    def is_ready(self) -> bool:
        with self._lock:
            return self._processes[self._current_job] == EmbeddingsPipelineStatus.READY

    def is_running(self) -> bool:
        with self._lock:
            return self._processes[self._current_job] == EmbeddingsPipelineStatus.RUNNING

    def is_completed(self) -> bool:
        with self._lock:
            return self._processes[self._current_job] == EmbeddingsPipelineStatus.COMPLETED

    def is_failed(self) -> bool:
        with self._lock:
            return self._processes[self._current_job] == EmbeddingsPipelineStatus.FAILED

    def is_idle(self) -> bool:
        with self._lock:
            return self._processes[self._current_job] in {
                EmbeddingsPipelineStatus.READY,
                EmbeddingsPipelineStatus.COMPLETED,
                EmbeddingsPipelineStatus.FAILED,
            }

    # ---------------- Job queries ---------------- #

    def has_job(self, job_id: str) -> bool:
        with self._lock:
            return job_id in self._processes

    def get_error(self, job_id: str) -> Optional[str]:
        with self._lock:
            return self._errors.get(job_id)

    def get_jobs_list(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [self.get_status(job_id) for job_id in self._processes]

    def get_current_status(self) -> Dict[str, Any]:
        with self._lock:
            return self.get_status(self._current_job)

    def get_status(self, job_id: str) -> Dict[str, object]:
        with self._lock:
            return {
                "job_id": job_id,
                "job_status": self._processes.get(job_id, "unknown"),
                "job_last_error": self._errors.get(job_id)
            }

    # ---------------- Reindex launcher ----------------- #
    def reindex(self):
        return reindex_search_indexes()

    # ---------------- Execution control ---------------- #

    def start(self) -> bool:
        """Start a new embeddings job in a background thread."""
        if not self.is_idle():
            return False

        Thread(target=self._run_embeddings_process, daemon=True).start()
        return True

    def _run_embeddings_process(self) -> None:
        try:
            with self._lock:
                # Only reuse job if still in READY
                if not self.is_ready():
                    self._current_job = str(uuid.uuid4())
                self._processes[self._current_job] = EmbeddingsPipelineStatus.RUNNING
                self._errors[self._current_job] = None

            # ###############################################################
            # Calling the actual embeddings processing logic here.
            from analytics.sc_embeddings import create_product_embeddings_w2v
            from analytics.sc_session import get_session
            session = get_session()
            try:
                create_product_embeddings_w2v(session)
            except Exception as e:
                raise e from e
            finally:
                session.stop()
            # ###############################################################

            with self._lock:
                self._processes[self._current_job] = EmbeddingsPipelineStatus.COMPLETED

        except Exception as e:
            with self._lock:
                self._errors[self._current_job] = str(e)
                self._processes[self._current_job] = EmbeddingsPipelineStatus.FAILED
