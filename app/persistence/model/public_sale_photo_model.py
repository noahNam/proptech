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
    public_sales_id = Column(BigInteger,
                             ForeignKey(PublicSaleModel.id, ondelete="CASCADE"),
                             nullable=False,
                             unique=True)

    file_name = Column(String(20), nullable=False)
    path = Column(String(150), nullable=False)
    extension = Column(String(4), nullable=False)
    created_at = Column(DateTime, default=get_server_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=get_server_timestamp(), nullable=False)

    def __repr__(self):
        return (
            f"PublicSalePhoto({self.id}, "
            f"{self.public_sales_id}, "
            f"{self.file_name}, "
            f"{self.path}, "
            f"{self.extension}, "
            f"{self.created_at}, "
            f"{self.updated_at}) "
        )

    def to_entity(self) -> PublicSalePhotoEntity:
        return PublicSalePhotoEntity(
            id=self.id,
            public_sales_id=self.public_sales_id,
            file_name=self.file_name,
            path=S3Helper.get_s3_url() + "/" + self.path,
            extension=self.extension,
            created_at=self.created_at.date().strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=self.updated_at.date().strftime("%Y-%m-%d %H:%M:%S")
        )
