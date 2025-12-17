from slowapi import Limiter
from slowapi.util import get_remote_address

# Лимитер, привязанный к IP адресу
limiter = Limiter(key_func=get_remote_address)
