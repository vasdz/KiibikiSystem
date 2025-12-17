from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    actor_id: Optional[int] = Field(default=None)  # Кто сделал (может быть Null при неудачном входе)
    action: str  # Тип действия (LOGIN, REWARD, ALERT)
    details: str  # IP, UserAgent, суть действия
    timestamp: datetime = Field(default_factory=datetime.utcnow)
