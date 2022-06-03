from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    DateTime,
    Boolean,
    SmallInteger,
    func,
)

from app import db
from app.extensions.utils.image_helper import S3Helper
from core.domains.house.entity.house_entity import HousePhotoEntity


class HousePhotoModel(db.Model):
    __tablename__ = "house_photos"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        nullable=False,
    )
    private_sale_id = Column(
        BigInteger().with_variant(Integer, "sqlite"), nullable=False, index=True,
    )

    file_name = Column(String(20), nullable=False)
    path = Column(String(150), nullable=False)
    extension = Column(String(4), nullable=False)
    is_thumbnail = Column(Boolean, nullable=False, default=False)
    seq = Column(SmallInteger, nullable=False, autoincrement=True, default=0)
    is_available = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def to_entity(self) -> HousePhotoEntity:
        return HousePhotoEntity(
            id=self.id,
            private_sale_id=self.private_sale_id,
            file_name=self.file_name,
            path=S3Helper.get_cloudfront_url() + "/" + self.path if self.path else None,
            extension=self.extension,
            is_thumbnail=self.is_thumbnail,
            seq=self.seq,
            is_available=self.is_available,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
