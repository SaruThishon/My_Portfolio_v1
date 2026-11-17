"""Activity logging utility — records admin events to activity_logs table."""
import logging
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.activity import ActivityLog

logger = logging.getLogger(__name__)


async def log_activity(
    db: AsyncSession,
    action: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    description: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
) -> None:
    """
    Log an administrative action. Silently ignores failures so
    a logging error never breaks the main operation.
    """
    try:
        log = ActivityLog(
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id else None,
            description=description,
            extra_data=metadata,
            ip_address=ip_address,
        )
        db.add(log)
        await db.commit()
    except Exception as e:
        logger.error(f"Activity log failed for action '{action}': {e}")
