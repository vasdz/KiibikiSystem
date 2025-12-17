import shutil
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.modules.proofs.models import Proof, ProofStatus

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Сигнатуры безопасных файлов (Hex заголовки)
ALLOWED_MAGIC_NUMBERS = {
    b'\xFF\xD8\xFF': "jpg",  # JPEG
    b'\x89\x50\x4E\x47': "png",  # PNG
    b'\x25\x50\x44\x46': "pdf"  # PDF
}


async def validate_file_header(file: UploadFile):
    """Проверяет реальный тип файла по байтам, а не по расширению"""
    # Читаем первые 4 байта
    header = await file.read(4)
    # ОБЯЗАТЕЛЬНО возвращаем каретку в начало, иначе файл сохранится пустым
    await file.seek(0)

    is_valid = False
    for magic, ext in ALLOWED_MAGIC_NUMBERS.items():
        if header.startswith(magic):
            is_valid = True
            break

    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Security Alert: Invalid file format. Only JPG, PNG, PDF allowed."
        )


async def save_proof_file(file: UploadFile, user_id: int, description: str, session) -> Proof:
    # 1. Проверка на вирусы/скрипты
    await validate_file_header(file)

    # 2. Генерируем безопасное имя
    file_ext = file.filename.split(".")[-1]
    safe_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = UPLOAD_DIR / safe_filename

    # 3. Сохраняем на диск
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 4. Записываем в БД
    proof = Proof(
        user_id=user_id,
        filename=file.filename,
        file_path=str(file_path),
        description=description,
        status=ProofStatus.PENDING
    )
    session.add(proof)
    await session.commit()
    await session.refresh(proof)
    return proof
