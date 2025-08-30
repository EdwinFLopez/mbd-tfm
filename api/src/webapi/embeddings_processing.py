import threading
import time
import uuid
from enum import Enum
from threading import Thread
from typing import Dict


class EmbeddingsPipelineStatus(str, Enum):
    """
    Enumeration of the possible status of the embeddings processing job.
    """
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class PipelineProcessor:
    """
    Helper class to manage embeddings processing job status.
    """

    def __init__(self):
        self.process_lock = threading.Lock()
        self._current_job: str = str(uuid.uuid4())
        self._errors: dict[str, str | None] = { self._current_job: None }
        self._processes: dict[str, EmbeddingsPipelineStatus] = { self._current_job: EmbeddingsPipelineStatus.READY }

    def is_ready(self) -> bool:
        return self._processes[self._current_job] == EmbeddingsPipelineStatus.READY

    def is_running(self) -> bool:
        return self._processes[self._current_job] == EmbeddingsPipelineStatus.RUNNING

    def is_completed(self) -> bool:
        return self._processes[self._current_job] == EmbeddingsPipelineStatus.COMPLETED

    def is_failed(self) -> bool:
        return self._processes[self._current_job] == EmbeddingsPipelineStatus.FAILED

    def is_idle(self) -> bool:
        return self._processes[self._current_job] in [
            EmbeddingsPipelineStatus.COMPLETED,
            EmbeddingsPipelineStatus.FAILED,
            EmbeddingsPipelineStatus.READY
        ]

    def has_job(self, job_id: str) -> bool:
        return job_id in self._processes.keys()

    def get_error(self, p_id: str) -> str | None:
        if p_id in self._errors.keys():
            return self._errors[p_id]
        return None

    def get_jobs_list(self) -> list[dict[str, object]]:
        return [ self.get_status(job_id) for job_id in self._processes.keys()]

    def get_current_status(self) -> dict[str, str | EmbeddingsPipelineStatus | None] | None:
        return self.get_status(self._current_job)

    def get_status(self, p_id: str) -> dict[str, str | EmbeddingsPipelineStatus | None] | None:
        if p_id in self._processes.keys():
            return {
                'job_id': p_id,
                'job_status': self._processes[p_id],
                'job_last_error': self.get_error(p_id)
            }
        return None

    def start(self) -> bool | None:
        if self.is_idle():
            thread: Thread = Thread(target=self.__run_embeddings_process__, daemon=True)
            thread.start()
            return True
        return False

    def __run_embeddings_process__(self) -> None:
        try:
            with self.process_lock:
                self._current_job = self._current_job if self.is_ready() else str(uuid.uuid4())
                self._processes[self._current_job] = EmbeddingsPipelineStatus.RUNNING

            time.sleep(40)  # call spark embeddings processor

            with self.process_lock:
                self._processes[self._current_job] = EmbeddingsPipelineStatus.COMPLETED
        except Exception as e:
            with self.process_lock:
                self._errors[self._current_job] = str(e)
                self._processes[self._current_job] = EmbeddingsPipelineStatus.FAILED
