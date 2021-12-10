from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    SmallInteger,
    BigInteger,
    ForeignKey,
    Unicode, func,
)

from app import db
from app.persistence.model.post_model import PostModel
from core.domains.post.entity.post_entity import ArticleEntity


class ArticleModel(db.Model):
    __tablename__ = "articles"

    id = Column(SmallInteger().with_variant(Integer, "sqlite"), primary_key=True)
    post_id = Column(
        BigInteger, ForeignKey(PostModel.id), nullable=False, unique=True, index=True,
    )
    body = Column(Unicode, nullable=True)
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def to_entity(self) -> ArticleEntity:
        return ArticleEntity(body=self.body,)
