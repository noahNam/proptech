from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    ForeignKey,
    String,
    DateTime,
    func,
)

from app import db
from app.extensions.utils.image_helper import S3Helper
from app.persistence.model.public_sale_detail_model import PublicSaleDetailModel
from core.domains.house.entity.house_entity import PublicSaleDetailPhotoEntity


class PublicSaleDetailPhotoModel(db.Model):
    __tablename__ = "public_sale_detail_photos"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    public_sale_detail_id = Column(
        BigInteger,
        ForeignKey(PublicSaleDetailModel.id),
        nullable=False,
        unique=True,
        index=True,
    )

    file_name = Column(String(20), nullable=False)
    path = Column(String(150), nullable=False)
    extension = Column(String(4), nullable=False)
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def to_entity(self) -> PublicSaleDetailPhotoEntity:
        return PublicSaleDetailPhotoEntity(
            id=self.id,
            public_sale_detail_id=self.public_sale_detail_id,
            file_name=self.file_name,
            path=S3Helper.get_cloudfront_url() + "/" + self.path if self.path else None,
            extension=self.extension,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
