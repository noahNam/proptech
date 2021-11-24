from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    DateTime,
    SmallInteger,
    String,
    Boolean,
)
from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.report.entity.report_entity import SurveyResultEntity


class SurveyResultModel(db.Model):
    __tablename__ = "survey_results"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    total_point = Column(SmallInteger, nullable=True)
    detail_point_house = Column(SmallInteger, nullable=True)
    detail_point_family = Column(SmallInteger, nullable=True)
    detail_point_bank = Column(SmallInteger, nullable=True)
    public_newly_married = Column(SmallInteger, nullable=True)
    public_married_income_point = Column(SmallInteger, nullable=True)
    public_married_child_point = Column(SmallInteger, nullable=True)
    public_married_address_point = Column(SmallInteger, nullable=True)
    public_married_bank_point = Column(SmallInteger, nullable=True)
    public_married_date_point = Column(SmallInteger, nullable=True)
    private_married_child_num = Column(SmallInteger, nullable=True)
    private_married_rank = Column(SmallInteger, nullable=True)
    public_newly_married_div = Column(String(2), nullable=True)
    public_first_life = Column(Boolean, nullable=True)
    public_first_life_div = Column(String(2), nullable=True)
    public_multiple_children = Column(SmallInteger, nullable=True)
    public_old_parent = Column(SmallInteger, nullable=True)
    public_agency_recommend = Column(SmallInteger, nullable=True)
    public_normal = Column(SmallInteger, nullable=True)
    private_newly_married = Column(SmallInteger, nullable=True)
    private_newly_married_div = Column(String(2), nullable=True)
    private_first_life = Column(Boolean, nullable=True)
    private_first_life_div = Column(String(2), nullable=True)
    private_multiple_children = Column(SmallInteger, nullable=True)
    private_old_parent = Column(SmallInteger, nullable=True)
    private_agency_recommend = Column(SmallInteger, nullable=True)
    private_normal = Column(SmallInteger, nullable=True)
    hope_town_phase_one = Column(SmallInteger, nullable=True)
    hope_town_phase_two = Column(SmallInteger, nullable=True)
    hope_one_income_point = Column(SmallInteger, nullable=True)
    hope_one_address_point = Column(SmallInteger, nullable=True)
    hope_one_bank_point = Column(SmallInteger, nullable=True)
    hope_two_child_point = Column(SmallInteger, nullable=True)
    hope_two_household_point = Column(SmallInteger, nullable=True)
    hope_two_address_point = Column(SmallInteger, nullable=True)
    hope_two_bank_point = Column(SmallInteger, nullable=True)
    created_at = Column(
        DateTime(timezone=True), default=get_server_timestamp(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), default=get_server_timestamp(), nullable=False
    )

    def to_entity(self) -> SurveyResultEntity:
        return SurveyResultEntity(
            id=self.id,
            user_id=self.user_id,
            total_point=self.total_point,
            detail_point_house=self.detail_point_house,
            detail_point_family=self.detail_point_family,
            detail_point_bank=self.detail_point_bank,
            public_newly_married=self.public_newly_married,
            public_married_income_point=self.public_married_income_point,
            public_married_child_point=self.public_married_child_point,
            public_married_address_point=self.public_married_address_point,
            public_married_bank_point=self.public_married_bank_point,
            public_married_date_point=self.public_married_date_point,
            private_married_child_num=self.private_married_child_num,
            private_married_rank=self.private_married_rank,
            public_newly_married_div=self.public_newly_married_div,
            public_first_life=self.public_first_life,
            public_first_life_div=self.public_first_life_div,
            public_multiple_children=self.public_multiple_children,
            public_old_parent=self.public_old_parent,
            public_agency_recommend=self.public_agency_recommend,
            public_normal=self.public_normal,
            private_newly_married=self.private_newly_married,
            private_newly_married_div=self.private_newly_married_div,
            private_first_life=self.private_first_life,
            private_first_life_div=self.private_first_life_div,
            private_multiple_children=self.private_multiple_children,
            private_old_parent=self.private_old_parent,
            private_agency_recommend=self.private_agency_recommend,
            private_normal=self.private_normal,
            hope_town_phase_one=self.hope_town_phase_one,
            hope_town_phase_two=self.hope_town_phase_two,
            hope_one_income_point=self.hope_one_income_point,
            hope_one_address_point=self.hope_one_address_point,
            hope_one_bank_point=self.hope_one_bank_point,
            hope_two_child_point=self.hope_two_child_point,
            hope_two_household_point=self.hope_two_household_point,
            hope_two_address_point=self.hope_two_address_point,
            hope_two_bank_point=self.hope_two_bank_point,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
