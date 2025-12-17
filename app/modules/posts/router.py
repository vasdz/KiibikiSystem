import shutil
import os
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, Field, SQLModel
from app.core.db import get_session
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User

router = APIRouter()

UPLOAD_DIR = "uploads/posts"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class Post(SQLModel, table=True):
    __tablename__ = "posts"
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    author_id: int

@router.get("/", response_model=List[Post])
async def get_posts(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    return result.scalars().all()

@router.post("/")
async def create_post(
    title: str = Form(...),
    content: str = Form(...),
    image: UploadFile = File(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    if current_user.role != "admin":
         raise HTTPException(status_code=403, detail="Нет прав")

    image_path = None
    if image:
        # Сохраняем файл так, чтобы его можно было раздать через StaticFiles
        filename = f"{datetime.now().timestamp()}_{image.filename}"
        file_location = f"{UPLOAD_DIR}/{filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        # Формируем URL (предполагаем, что uploads раздается по /static)
        image_path = f"/static/posts/{filename}"

    new_post = Post(title=title, content=content, image_url=image_path, author_id=current_user.id)
    session.add(new_post)
    await session.commit()
    await session.refresh(new_post)
    return new_post

@router.delete("/{post_id}")
async def delete_post(post_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    post = await session.get(Post, post_id)
    if not post: raise HTTPException(status_code=404)
    if current_user.role != "admin": raise HTTPException(status_code=403)
    await session.delete(post)
    await session.commit()
    return {"ok": True}
