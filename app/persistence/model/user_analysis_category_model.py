from sqlalchemy import (
    Column,
    Integer,
    String,
    SmallInteger,
    Text,
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

    user_analysis_category_details = relationship(
        "UserAnalysisCategoryDetailModel",
        backref="user_analysis_categories",
        uselist=True,
    )

    def to_entity(self) -> UserAnalysisCategoryEntity:
        return UserAnalysisCategoryEntity(
            id=self.id,
            div=self.div,
            category=self.category,
            title=self.title,
            output_text=self.output_text,
            user_analysis_category_details=[
                user_analysis_category_detail.to_entity()
                for user_analysis_category_detail in self.user_analysis_category_details
            ]
            if self.user_analysis_category_details
            else None,
        )
