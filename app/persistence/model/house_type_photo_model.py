from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    DateTime,
    Boolean,
    func,
)

from app import db
from app.extensions.utils.image_helper import S3Helper
from core.domains.house.entity.house_entity import HouseTypePhotoEntity


class HouseTypePhotoModel(db.Model):
    __tablename__ = "house_type_photos"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False,
    )
    private_sale_id = Column(
        BigInteger().with_variant(Integer, "sqlite"), nullable=False, index=True,
    )
    type_name = Column(String(20), nullable=False)
    file_name = Column(String(20), nullable=False)
    path = Column(String(150), nullable=False)
    extension = Column(String(4), nullable=False)
    is_available = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def to_entity(self) -> HouseTypePhotoEntity:
        return HouseTypePhotoEntity(
            id=self.id,
            private_sale_id=self.private_sale_id,
            type_name=self.file_name,
            file_name=self.file_name,
            path=S3Helper.get_cloudfront_url() + "/" + self.path if self.path else None,
            extension=self.extension,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
