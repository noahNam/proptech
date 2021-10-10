from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    ForeignKey,
    String,
    DateTime,
)

from app import db
from app.extensions.utils.image_helper import S3Helper
from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model.public_sale_model import PublicSaleModel
from core.domains.house.entity.house_entity import PublicSalePhotoEntity


class PublicSalePhotoModel(db.Model):
    __tablename__ = "public_sale_photos"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    public_sales_id = Column(
        BigInteger,
        ForeignKey(PublicSaleModel.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    file_name = Column(String(20), nullable=False)
    path = Column(String(150), nullable=False)
    extension = Column(String(4), nullable=False)
    created_at = Column(DateTime, default=get_server_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=get_server_timestamp(), nullable=False)

    def to_entity(self) -> PublicSalePhotoEntity:
        return PublicSalePhotoEntity(
            id=self.id,
            public_sales_id=self.public_sales_id,
            file_name=self.file_name,
            path=S3Helper.get_cloudfront_url() + "/" + self.path if self.path else None,
            extension=self.extension,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
