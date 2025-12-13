from pydantic import BaseModel
from typing import Optional

class Alert(BaseModel):
    id: str
    severity: str
    service: str
    metric: str
    value: float
    threshold: float
    timestamp: str
    host: Optional[str] = None
