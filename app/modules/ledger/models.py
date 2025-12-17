from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class Transaction(SQLModel, table=True):
    __tablename__ = "ledger_transactions"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Ссылки
    target_user_id: int = Field(index=True)  # Кому начислили (студент)
    admin_id: int = Field(index=True)  # Кто начислил (сотрудник)

    # Финансы
    amount: int  # Может быть плюс (награда) или минус (покупка)
    reason: str  # За что (например, "Победа в CTF")

    # Криптография
    prev_hash: str = Field(index=True)  # Хеш предыдущей записи (связь цепочки)
    signature: str  # Подпись админа (Ed25519)
    current_hash: str = Field(unique=True)  # Хеш текущей записи

    created_at: datetime = Field(default_factory=datetime.utcnow)
