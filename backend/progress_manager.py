from threading import Lock
from typing import List, Optional
from models import ProgressTask, TaskStatus
from datetime import datetime
import uuid

class ProgressManager:
    def __init__(self):
        self._lock = Lock()
        self._tasks: List[ProgressTask] = []
        self.is_running = False

    def reset(self):
        with self._lock:
            self._tasks = []
            self.is_running = False

    def start(self, tasks: List[dict]):
        with self._lock:
            self._tasks = [
                ProgressTask(
                    id=f"{t['email']}|{t['url']}",
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    **t
                )
                for t in tasks
            ]
            self.is_running = True

    def update_task(self, task_id: str, status: TaskStatus, message: Optional[str] = None):
        with self._lock:
            for task in self._tasks:
                if task.id == task_id:
                    task.status = status
                    task.updated_at = datetime.now()
                    if message:
                        task.message = message
                    break

    def get_tasks(self) -> List[ProgressTask]:
        with self._lock:
            return list(self._tasks)

    def get_status(self):
        with self._lock:
            total = len(self._tasks)
            completed = sum(1 for t in self._tasks if t.status in [TaskStatus.ok, TaskStatus.error, TaskStatus.captcha])
            return {
                "is_running": self.is_running,
                "total": total,
                "completed": completed
            }

progress_manager = ProgressManager()
