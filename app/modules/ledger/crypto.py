import hashlib
import json
from nacl.signing import SigningKey, VerifyKey
from nacl.encoding import HexEncoder
from datetime import datetime


# 1. Хеширование данных транзакции
def calculate_hash(prev_hash: str, target_user_id: int, amount: int, reason: str, timestamp: str) -> str:
    """Создает уникальный отпечаток транзакции, зависящий от предыдущей"""
    data_string = f"{prev_hash}|{target_user_id}|{amount}|{reason}|{timestamp}"
    return hashlib.sha256(data_string.encode()).hexdigest()


# 2. Генерация пары ключей (Запустишь это один раз, чтобы создать ключи для Арутюновой и др.)
def generate_key_pair():
    signing_key = SigningKey.generate()
    verify_key = signing_key.verify_key

    private_hex = signing_key.encode(encoder=HexEncoder).decode()
    public_hex = verify_key.encode(encoder=HexEncoder).decode()

    return {"private_key": private_hex, "public_key": public_hex}


# 3. Подпись данных (Делает Админ своим приватным ключом)
def sign_data(private_key_hex: str, data_hash: str) -> str:
    signing_key = SigningKey(private_key_hex, encoder=HexEncoder)
    signed = signing_key.sign(data_hash.encode(), encoder=HexEncoder)
    return signed.decode()  # Возвращает подпись


# 4. Проверка подписи (Делает Система публичным ключом Админа)
def verify_signature(public_key_hex: str, data_hash: str, signature_hex: str) -> bool:
    try:
        verify_key = VerifyKey(public_key_hex, encoder=HexEncoder)
        verify_key.verify(data_hash.encode(), signature_hex.encode(encoder=HexEncoder))
        return True
    except Exception:
        return False
