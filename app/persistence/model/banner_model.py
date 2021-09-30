from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Boolean,
    SmallInteger,
)
from sqlalchemy.orm import relationship

from app import db
from core.domains.banner.entity.banner_entity import BannerEntity


class BannerModel(db.Model):
    __tablename__ = "banners"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    title = Column(String(50), nullable=False)
    desc = Column(String(100), nullable=True)
    section_type = Column(SmallInteger, nullable=False)
    sub_topic = Column(SmallInteger, nullable=False)
    contents_num = Column(SmallInteger, nullable=False)
    reference_url = Column(String(150), nullable=True)
    is_active = Column(Boolean, nullable=False, default=False)
    is_event = Column(Boolean, nullable=False, default=False)

    banner_image = relationship("BannerImageModel", backref="banner", uselist=False)

    def to_entity(self) -> BannerEntity:
        return BannerEntity(
            id=self.id,
            title=self.title,
            desc=self.desc,
            section_type=self.section_type,
            sub_topic=self.sub_topic,
            contents_num=self.contents_num,
            reference_url=self.reference_url,
            banner_image=self.banner_image.to_entity() if self.banner_image else None,
            is_active=self.is_active,
            is_event=self.is_event,
        )
