from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    DateTime,
    SmallInteger,
    ForeignKey,
    func,
)

from app import db
from app.extensions.utils.image_helper import S3Helper
from app.persistence.model import PostModel
from core.domains.post.entity.post_entity import PostAttachmentEntity


class PostAttachmentModel(db.Model):
    __tablename__ = "post_attachments"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    post_id = Column(BigInteger, ForeignKey(PostModel.id), nullable=False, index=True,)
    type = Column(SmallInteger, default=0, nullable=False)
    file_name = Column(String(50), nullable=False)
    path = Column(String(150), nullable=False)
    extension = Column(String(4), nullable=False)
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def to_entity(self) -> PostAttachmentEntity:
        return PostAttachmentEntity(
            id=self.id,
            post_id=self.post_id,
            type=self.type,
            file_name=self.file_name,
            path=S3Helper.get_cloudfront_url() + "/" + self.path,
            extension=self.extension,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
