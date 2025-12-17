from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List
from pydantic import BaseModel

from app.core.db import get_session
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.audit.service import log_action

# --- ИСПРАВЛЕНИЕ: Импортируем модель, а не определяем её заново ---
from app.modules.ledger.models import Transaction

router = APIRouter()


# Pydantic-схема для входных данных (её оставляем тут или выносим в schemas.py)
class TransactionCreate(BaseModel):
    username: str
    amount: int
    reason: str


# --- Роуты ---

@router.post("/accrue")
async def accrue_points(
        tx_data: TransactionCreate,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session)
):
    # 1. Только админ может начислять
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Только администратор может начислять баллы")

    # 2. Ищем студента
    result = await session.execute(select(User).where(User.username == tx_data.username))
    student = result.scalars().first()
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")

    # 3. Обновляем баланс
    student.balance += tx_data.amount

    # 4. Создаем запись в истории
    new_tx = Transaction(
        user_id=student.id,
        amount=tx_data.amount,
        reason=tx_data.reason
    )

    session.add(new_tx)
    session.add(student)
    await session.commit()

    await log_action(session, "ACCRUE_POINTS",
                     f"Admin {current_user.username} gave {tx_data.amount} to {student.username}", current_user.id)

    return {"status": "success", "new_balance": student.balance}


@router.get("/history", response_model=List[Transaction])
async def get_my_history(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session)
):
    # Возвращаем историю только текущего пользователя
    result = await session.execute(
        select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .order_by(Transaction.created_at.desc())
    )
    return result.scalars().all()
