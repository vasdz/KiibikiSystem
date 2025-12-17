import shutil
import os
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User

router = APIRouter()  # Убрали префикс тут, так как он задается в main.py

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_achievement(
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_user)
):
    try:
        # Генерируем уникальное имя
        file_path = f"{UPLOAD_DIR}/{current_user.id}_{file.filename}"

        # Сохраняем файл на диск
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "status": "success",
            "filename": file.filename,
            "message": "Файл успешно загружен и отправлен на проверку"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки: {str(e)}")
