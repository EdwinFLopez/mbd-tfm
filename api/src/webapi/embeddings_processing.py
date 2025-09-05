import threading
import time
import uuid
from enum import Enum
from threading import Thread
from typing import Dict, Optional, List


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
        self._lock = threading.Lock()
        self._current_job: str = str(uuid.uuid4())
        self._errors: Dict[str, Optional[str]] = {
            self._current_job: None
        }
        self._processes: Dict[str, EmbeddingsPipelineStatus] = {
            self._current_job: EmbeddingsPipelineStatus.READY
        }

    # ---------------- Status helpers ---------------- #
    def release(self) -> None:
        if self._lock.locked():
            self._lock.release()

    # ---------------- Status helpers ---------------- #

    def is_ready(self) -> bool:
        return self._processes[self._current_job] == EmbeddingsPipelineStatus.READY

    def is_running(self) -> bool:
        return self._processes[self._current_job] == EmbeddingsPipelineStatus.RUNNING

    def is_completed(self) -> bool:
        return self._processes[self._current_job] == EmbeddingsPipelineStatus.COMPLETED

    def is_failed(self) -> bool:
        return self._processes[self._current_job] == EmbeddingsPipelineStatus.FAILED

    def is_idle(self) -> bool:
        return self._processes[self._current_job] in {
            EmbeddingsPipelineStatus.READY,
            EmbeddingsPipelineStatus.COMPLETED,
            EmbeddingsPipelineStatus.FAILED,
        }

    # ---------------- Job queries ---------------- #

    def has_job(self, job_id: str) -> bool:
        return job_id in self._processes

    def get_error(self, job_id: str) -> Optional[str]:
        return self._errors.get(job_id)

    def get_jobs_list(self) -> List[Dict[str, object]]:
        return [self.get_status(job_id) for job_id in self._processes]

    def get_current_status(self) -> Dict[str, object]:
        with self._lock:
            return self.get_status(self._current_job)

    def get_status(self, job_id: str) -> Dict[str, object]:
        return {
            "job_id": job_id,
            "job_status": self._processes.get(job_id, "unknown"),
            "job_last_error": self._errors.get(job_id),
        }

    # ---------------- Execution control ---------------- #

    def start(self) -> bool:
        """Start a new embeddings job in a background thread."""
        if not self.is_idle():
            return False

        Thread(target=self.__run_embeddings_process__, daemon=True).start()
        return True

    def __run_embeddings_process__(self) -> None:
        try:
            with self._lock:
                # Only reuse job if it’s still in READY
                if not self.is_ready():
                    self._current_job = str(uuid.uuid4())
                self._processes[self._current_job] = EmbeddingsPipelineStatus.RUNNING
                self._errors[self._current_job] = None

            # ###############################################################
            # Call the actual embeddings processing logic here.
            # This is a placeholder for the real implementation.
            # ###############################################################
            time.sleep(40)
            # ###############################################################

            with self._lock:
                self._processes[self._current_job] = EmbeddingsPipelineStatus.COMPLETED

        except Exception as e:
            with self._lock:
                self._errors[self._current_job] = str(e)
                self._processes[self._current_job] = EmbeddingsPipelineStatus.FAILED
