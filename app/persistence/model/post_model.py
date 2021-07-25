from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Boolean,
    SmallInteger,
)
from sqlalchemy.orm import relationship

from app import db
from app.extensions.utils.time_helper import get_server_timestamp

from app.persistence.model.user_model import UserModel
from core.domains.post.entity.post_entity import PostEntity


class PostModel(db.Model):
    __tablename__ = "posts"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    user_id = Column(BigInteger, ForeignKey(UserModel.id), nullable=False)
    title = Column(String(50), nullable=False)
    type = Column(String(10), nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    read_count = Column(Integer, default=0, nullable=False)
    category_id = Column(SmallInteger, nullable=False, index=True)
    last_admin_action = Column(String(10), nullable=True)
    last_admin_action_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=get_server_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=get_server_timestamp(), nullable=False)

    user = relationship("UserModel", backref="post", uselist=False)
    article = relationship("ArticleModel", backref="post", uselist=False)

    def to_entity(self) -> PostEntity:
        return PostEntity(
            id=self.id,
            user_id=self.user_id,
            title=self.title,
            body=self.article.body if self.article else None,
            type=self.type,
            is_deleted=self.is_deleted,
            read_count=self.read_count,
            last_admin_action=self.last_admin_action,
            last_admin_action_at=self.last_admin_action_at,
            created_at=self.created_at.date().strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=self.updated_at.date().strftime("%Y-%m-%d %H:%M:%S"),
            user=self.user.to_entity() if self.user else None,
            category_id=self.category_id,
        )
