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
from core.domains.house.entity.house_entity import PublicSaleDetailPhotoEntity
from app.persistence.model.public_sale_detail_model import PublicSaleDetailModel


class PublicSaleDetailPhotoModel(db.Model):
    __tablename__ = "public_sale_detail_photos"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    public_sale_details_id = Column(
        BigInteger,
        ForeignKey(PublicSaleDetailModel.id, ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    file_name = Column(String(20), nullable=False)
    path = Column(String(150), nullable=False)
    extension = Column(String(4), nullable=False)
    created_at = Column(DateTime, default=get_server_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=get_server_timestamp(), nullable=False)

    def to_entity(self) -> PublicSaleDetailPhotoEntity:
        return PublicSaleDetailPhotoEntity(
            id=self.id,
            public_sale_details_id=self.public_sale_details_id,
            file_name=self.file_name,
            path=S3Helper.get_s3_url() + "/" + self.path,
            extension=self.extension,
            created_at=self.created_at.date().strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=self.updated_at.date().strftime("%Y-%m-%d %H:%M:%S"),
        )
