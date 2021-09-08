from sqlalchemy import (
    Column,
    Integer,
    String,
    SmallInteger,
    Text,
    Boolean,
)
from sqlalchemy.orm import relationship

from app import db
from core.domains.report.entity.report_entity import UserAnalysisCategoryEntity


class UserAnalysisCategoryModel(db.Model):
    __tablename__ = "user_analysis_categories"

    id = Column(SmallInteger().with_variant(Integer, "sqlite"), primary_key=True)
    div = Column(String(1), nullable=False)
    category = Column(SmallInteger, nullable=False)
    title = Column(String(20), nullable=False)
    output_text = Column(Text, nullable=False)
    seq = Column(SmallInteger, nullable=False)
    type = Column(String(1), nullable=False)
    is_active = Column(Boolean, nullable=False)

    user_analysis_category_detail = relationship(
        "UserAnalysisCategoryDetailModel",
        backref="user_analysis_categories",
        uselist=False,
    )

    def to_entity(self) -> UserAnalysisCategoryEntity:
        return UserAnalysisCategoryEntity(
            id=self.id,
            div=self.div,
            category=self.category,
            title=self.title,
            output_text=self.output_text,
            user_analysis_category_detail=self.user_analysis_category_detail.to_entity()
            if self.user_analysis_category_detail
            else None,
            seq=self.seq,
            type=self.type,
            is_active=self.is_active,
        )
