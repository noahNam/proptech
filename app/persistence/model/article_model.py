from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    SmallInteger,
    BigInteger,
    ForeignKey,
    Unicode,
)

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model.post_model import PostModel
from core.domains.post.entity.article_entity import ArticleEntity


class ArticleModel(db.Model):
    __tablename__ = "articles"

    id = Column(SmallInteger().with_variant(Integer, "sqlite"), primary_key=True)
    post_id = Column(BigInteger, ForeignKey(PostModel.id), nullable=False, unique=True)
    body = Column(Unicode, nullable=True)
    created_at = Column(DateTime, default=get_server_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=get_server_timestamp(), nullable=False)

    def to_entity(self) -> ArticleEntity:
        return ArticleEntity(
            id=self.id,
            post_id=self.post_id,
            body=self.body,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
