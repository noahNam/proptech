from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    SmallInteger,
    String,
    Float,
)
from app import db
from core.domains.report.entity.report_entity import PredictedCompetitionEntity


class PredictedCompetitionModel(db.Model):
    __tablename__ = "predicted_competitions"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    ticket_usage_result_id = Column(BigInteger, nullable=False, index=True)
    house_structure_type = Column(String(10), nullable=False)
    private_area = Column(Float, nullable=True)
    supply_area = Column(Float, nullable=True)
    region = Column(String(5), nullable=False)
    region_percentage = Column(SmallInteger, nullable=False)
    multiple_children_competition = Column(Integer, nullable=True)
    newly_marry_competition = Column(Integer, nullable=True)
    old_parent_competition = Column(Integer, nullable=True)
    first_life_competition = Column(Integer, nullable=True)
    multiple_children_supply = Column(Integer, nullable=True)
    newly_marry_supply = Column(SmallInteger, nullable=True)
    old_parent_supply = Column(SmallInteger, nullable=True)
    first_life_supply = Column(SmallInteger, nullable=True)
    normal_competition = Column(Integer, nullable=True)
    normal_supply = Column(SmallInteger, nullable=True)
    normal_passing_score = Column(SmallInteger, nullable=True)

    def to_entity(self) -> PredictedCompetitionEntity:
        return PredictedCompetitionEntity(
            id=self.id,
            ticket_usage_result_id=self.ticket_usage_result_id,
            house_structure_type=self.house_structure_type,
            private_area=self.private_area,
            supply_area=self.supply_area,
            region=self.region,
            region_percentage=self.region_percentage,
            multiple_children_competition=self.multiple_children_competition,
            newly_marry_competition=self.newly_marry_competition,
            old_parent_competition=self.old_parent_competition,
            first_life_competition=self.first_life_competition,
            multiple_children_supply=self.multiple_children_supply,
            newly_marry_supply=self.newly_marry_supply,
            old_parent_supply=self.old_parent_supply,
            first_life_supply=self.first_life_supply,
            normal_competition=self.normal_competition,
            normal_supply=self.normal_supply,
            normal_passing_score=self.normal_passing_score,
        )
