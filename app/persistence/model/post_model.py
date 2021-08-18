from typing import List

from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    DateTime,
    Boolean,
    SmallInteger,
)
from sqlalchemy.orm import relationship

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.post.entity.post_entity import PostEntity, ArticleEntity


class PostModel(db.Model):
    __tablename__ = "posts"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    category_id = Column(SmallInteger, nullable=False, index=True)
    category_detail_id = Column(SmallInteger, nullable=False, index=True)
    title = Column(String(50), nullable=False)
    desc = Column(String(200), nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    read_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=get_server_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=get_server_timestamp(), nullable=False)

    article = relationship("ArticleModel", backref="post", uselist=False)
    post_attachments = relationship("PostAttachmentModel", backref="post", uselist=True)

    def to_entity(self, article: ArticleEntity) -> PostEntity:
        return PostEntity(
            id=self.id,
            title=self.title,
            desc=self.desc,
            category_id=self.category_id,
            category_detail_id=self.category_detail_id,
            body=article if self.article else None,
            post_attachments=[
                post_attachment.to_entity() for post_attachment in self.post_attachments
            ]
            if self.post_attachments
            else None,
            is_deleted=self.is_deleted,
            read_count=self.read_count,
            created_at=self.created_at.date().strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=self.updated_at.date().strftime("%Y-%m-%d %H:%M:%S"),
        )
