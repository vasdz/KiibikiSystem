from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc
from app.modules.ledger.models import Transaction
from app.modules.ledger.crypto import calculate_hash, sign_data
from app.modules.auth.models import User
from datetime import datetime

async def create_transaction(
        session: AsyncSession,
        target_user_id: int,
        admin_id: int,
        amount: int,
        reason: str,
        admin_private_key: str  # В реале ключ не должен летать по сети, но для MVP ок
):
    # 1. Ищем последнюю транзакцию (Genesis block logic)
    query = select(Transaction).order_by(desc(Transaction.id)).limit(1)
    result = await session.exec(query)
    last_tx = result.first()

    # Если это первая запись в истории вуза
    prev_hash = last_tx.current_hash if last_tx else "GENESIS_HASH_000000000000000000"

    # 2. Формируем данные
    timestamp_str = str(datetime.utcnow())
    current_hash = calculate_hash(prev_hash, target_user_id, amount, reason, timestamp_str)

    # 3. Подписываем (как будто это сделала Арутюнова В.Ю.)
    signature = sign_data(admin_private_key, current_hash)

    # 4. Сохраняем в Леджер
    new_tx = Transaction(
        target_user_id=target_user_id,
        admin_id=admin_id,
        amount=amount,
        reason=reason,
        prev_hash=prev_hash,
        signature=signature,
        current_hash=current_hash,
        created_at=datetime.utcnow()  # В идеале юзать тот же timestamp_str
    )

    session.add(new_tx)

    # 5. Обновляем баланс студента (кэш)
    student = await session.get(User, target_user_id)
    if student:
        student.balance += amount
        session.add(student)

    await session.commit()
    await session.refresh(new_tx)
    return new_tx
