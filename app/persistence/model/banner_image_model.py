from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    DateTime,
    ForeignKey,
)

from app import db
from app.extensions.utils.image_helper import S3Helper
from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model import BannerModel
from core.domains.banner.entity.banner_entity import BannerImageEntity


class BannerImageModel(db.Model):
    __tablename__ = "banner_images"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    banner_id = Column(
        BigInteger, ForeignKey(BannerModel.id), nullable=False, index=True,
    )
    file_name = Column(String(20), nullable=False)
    path = Column(String(150), nullable=False)
    extension = Column(String(4), nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=get_server_timestamp(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), default=get_server_timestamp(), nullable=False
    )

    def to_entity(self) -> BannerImageEntity:
        return BannerImageEntity(
            id=self.id,
            banner_id=self.banner_id,
            file_name=self.file_name,
            path=S3Helper.get_cloudfront_url() + "/" + self.path,
            extension=self.extension,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
