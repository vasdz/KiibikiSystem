from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from enum import Enum


class ProofStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Proof(SQLModel, table=True):
    __tablename__ = "proofs"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)

    filename: str
    file_path: str
    description: str

    status: ProofStatus = Field(default=ProofStatus.PENDING)
    admin_comment: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
