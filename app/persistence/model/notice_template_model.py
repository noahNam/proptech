from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    DateTime,
    Boolean,
)

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.notification.entity.notification_entity import NoticeTemplateEntity


class NoticeTemplateModel(db.Model):
    __tablename__ = "notice_templates"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    title = Column(String(100), nullable=False)
    content = Column(String(200), nullable=False)
    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=get_server_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=get_server_timestamp(), nullable=False)

    def to_entity(self) -> NoticeTemplateEntity:
        return NoticeTemplateEntity(
            id=self.id,
            title=self.title,
            content=self.content,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
