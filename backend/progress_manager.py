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
        self._stop_flag = False

    def reset(self):
        import os
        with self._lock:
            self._tasks = []
            self.is_running = False
            self._stop_flag = False
        # Remove o arquivo de flag externo, se existir
        try:
            if os.path.exists('stop.flag'):
                os.remove('stop.flag')
        except Exception:
            pass

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
            # Auto-stop quando todas as tasks terminaram
            if self.is_running and self._tasks:
                all_finished = all(
                    task.status in [TaskStatus.ok, TaskStatus.error, TaskStatus.captcha]
                    for task in self._tasks
                )
                if all_finished:
                    self.is_running = False

    def finish(self):
        """Força o fim da execução (chamado manualmente pelo automator)"""
        with self._lock:
            self.is_running = False
            self._stop_flag = True
        # Sinaliza parada criando flag externa (mantém compatibilidade)
        try:
            with open('stop.flag', 'w') as f:
                f.write('stop')
        except Exception:
            pass  # Falha silenciosa para não travar o sistema

    def set_stop_flag(self):
        """Sinaliza parada de forma thread-safe (pode ser chamada de fora)."""
        with self._lock:
            self._stop_flag = True
        try:
            with open('stop.flag', 'w') as f:
                f.write('stop')
        except Exception:
            pass

    def is_stopped(self):
        """Consulta thread-safe se foi sinalizado para parar (thread-safe + arquivo externo)."""
        import os
        with self._lock:
            if self._stop_flag:
                return True
        # Checa arquivo externo para robustez
        return os.path.exists('stop.flag')

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
