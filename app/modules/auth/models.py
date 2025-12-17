from typing import Optional
from enum import Enum
from sqlmodel import SQLModel, Field
from datetime import datetime


class UserRole(str, Enum):
    STUDENT = "student"
    ADMIN = "admin"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    # Здесь будет номер студака (43К0434) или логин админа
    username: str = Field(unique=True, index=True)

    full_name: str
    hashed_password: str
    role: UserRole = Field(default=UserRole.STUDENT)

    # Баланс КиИБиков (храним в юзере для кэширования, но считать будем по транзакциям)
    balance: int = Field(default=0)

    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Для студентов можно добавить группу
    group_number: Optional[str] = None
