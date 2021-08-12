from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    SmallInteger,
    Boolean,
)

from app import db
from core.domains.banner.entity.banner_entity import ButtonLinkEntity


class ButtonLinkModel(db.Model):
    __tablename__ = "button_links"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    title = Column(String(50), nullable=False)
    reference_url = Column(String(150), nullable=False)
    section_type = Column(SmallInteger, nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)

    def to_entity(self) -> ButtonLinkEntity:
        return ButtonLinkEntity(
            id=self.id,
            title=self.title,
            reference_url=self.reference_url,
            section_type=self.section_type,
            is_active=self.is_active,
        )
