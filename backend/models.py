from enum import Enum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskStatus(str, Enum):
    pending = "pending"
    ok = "ok"
    captcha = "captcha"
    error = "error"
    running = "running"
    no_email_field = "no_email_field"
    http_error = "http_error"
    unknown_result = "unknown_result"

class ProgressTask(BaseModel):
    id: str
    email: str
    url: str
    status: TaskStatus = TaskStatus.pending
    message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
