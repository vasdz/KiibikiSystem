from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.audit.models import AuditLog

async def log_action(session: AsyncSession, action: str, details: str, actor_id: int = None):
    """
    Записывает критическое действие в базу.
    Не блокирует основной поток (fire and forget в идеале, но пока await).
    """
    try:
        log = AuditLog(
            actor_id=actor_id,
            action=action,
            details=details
        )
        session.add(log)
        await session.commit()
    except Exception as e:
        print(f"CRITICAL: FAILED TO WRITE AUDIT LOG: {e}")
