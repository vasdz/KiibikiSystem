from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from pydantic import BaseModel
from typing import Optional

from app.core.db import get_session
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.limiter import limiter
from app.modules.auth.models import User, UserRole
from app.modules.audit.service import log_action
from app.modules.auth.dependencies import get_current_user

router = APIRouter()


# --- Модели данных (Pydantic) ---
class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    group_number: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None


# --- Роуты ---

@router.post("/register", response_model=User)
async def register_student(user_in: UserCreate, session: AsyncSession = Depends(get_session)):
    # 1. Проверяем существование
    result = await session.execute(select(User).where(User.username == user_in.username))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="User already exists")

    # 2. Создаем
    new_user = User(
        username=user_in.username,
        full_name=user_in.full_name,
        group_number=user_in.group_number,
        hashed_password=get_password_hash(user_in.password),
        role=UserRole.STUDENT,
        balance=0
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    await log_action(session, "REGISTER", f"New user: {user_in.username}", new_user.id)
    return new_user


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


# ВОТ ЭТОТ МЕТОД НУЖЕН ДЛЯ ОБНОВЛЕНИЯ ПРОФИЛЯ:
@router.patch("/me", response_model=User)
async def update_user_me(
        user_update: UserUpdate,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    if user_update.full_name:
        current_user.full_name = user_update.full_name

    if user_update.password:
        current_user.hashed_password = get_password_hash(user_update.password)

    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)

    await log_action(session, "UPDATE_PROFILE", "User updated profile", current_user.id)
    return current_user


@router.post("/login")
@limiter.limit("5/minute")
async def login(
        request: Request,
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(User).where(User.username == form_data.username))
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        await log_action(session, "LOGIN_FAILED", f"User: {form_data.username} | IP: {request.client.host}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    await log_action(session, "LOGIN_SUCCESS", f"IP: {request.client.host}", user.id)
    access_token = create_access_token(subject=user.username)
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}
