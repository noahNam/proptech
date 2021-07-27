from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    DateTime,
    SmallInteger,
)
from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.user.entity.user_entity import SurveyResultEntity


class SurveyResultModel(db.Model):
    __tablename__ = "survey_results"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    total_point = Column(SmallInteger, nullable=True)
    detail_point_house = Column(SmallInteger, nullable=True)
    detail_point_family = Column(SmallInteger, nullable=True)
    detail_point_bank = Column(SmallInteger, nullable=True)
    public_newly_married = Column(SmallInteger, nullable=True)
    public_first_life = Column(SmallInteger, nullable=True)
    public_multiple_children = Column(SmallInteger, nullable=True)
    public_old_parent = Column(SmallInteger, nullable=True)
    public_agency_recommend = Column(SmallInteger, nullable=True)
    public_normal = Column(SmallInteger, nullable=True)
    private_newly_married = Column(SmallInteger, nullable=True)
    private_first_life = Column(SmallInteger, nullable=True)
    private_multiple_children = Column(SmallInteger, nullable=True)
    private_old_parent = Column(SmallInteger, nullable=True)
    private_agency_recommend = Column(SmallInteger, nullable=True)
    private_normal = Column(SmallInteger, nullable=True)
    hope_town_phase_one = Column(SmallInteger, nullable=True)
    hope_town_phase_two = Column(SmallInteger, nullable=True)
    created_at = Column(DateTime, default=get_server_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=get_server_timestamp(), nullable=False)

    def to_entity(self) -> SurveyResultEntity:
        return SurveyResultEntity(
            id=self.id,
            user_id=self.user_id,
            title=self.title,
            body=self.article.body if self.article else None,
            type=self.type,
            is_deleted=self.is_deleted,
            read_count=self.read_count,
            last_admin_action=self.last_admin_action,
            last_admin_action_at=self.last_admin_action_at,
            created_at=self.created_at.date().strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=self.updated_at.date().strftime("%Y-%m-%d %H:%M:%S"),
            user=self.user.to_entity() if self.user else None,
            category_id=self.category_id,
        )
