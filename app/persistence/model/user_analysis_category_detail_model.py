from sqlalchemy import (
    Column,
    Integer,
    SmallInteger, Text, ForeignKey,
)

from app import db
from app.persistence.model.user_analysis_category_model import UserAnalysisCategoryModel
from core.domains.report.entity.report_entity import UserAnalysisCategoryDetailEntity


class UserAnalysisCategoryDetailModel(db.Model):
    __tablename__ = "user_analysis_category_details"

    id = Column(SmallInteger().with_variant(Integer, "sqlite"), primary_key=True)
    user_analysis_category_id = Column(SmallInteger, ForeignKey(UserAnalysisCategoryModel.id), nullable=False)
    format_text = Column(Text, nullable=False)

    def to_entity(self) -> UserAnalysisCategoryDetailEntity:
        return UserAnalysisCategoryDetailEntity(
            id=self.id,
            user_analysis_category_id=self.user_analysis_category_id,
            format_text=self.format_text,
        )
