"""Table to store logs."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

import peewee

from .database import BaseModel, db


class Log(BaseModel):
    """Model for a tag."""

    level = peewee.IntegerField(default=logging.INFO)
    content = peewee.CharField(max_length=2000)
    created_at = peewee.DateTimeField(default=datetime.now)

    @classmethod
    async def get_logs(
            cls, start: Optional[datetime] = None,
            level: int = logging.INFO, max_logs: Optional[int] = 1000) -> str:
        """Get logs of some level (or greater) from some date."""
        query = cls.select().where(cls.level >= level)
        if start:
            query = query.where(cls.created_at <= start)
        if max_logs:
            query = query.limit(max_logs)
        return ''.join(query)


db.create_tables([Log])
