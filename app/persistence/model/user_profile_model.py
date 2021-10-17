from sqlalchemy import (
    Column,
    BigInteger,
    DateTime,
    Integer,
    ForeignKey,
    String,
    SmallInteger,
)
from sqlalchemy.orm import relationship, backref

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model import UserModel
from core.domains.user.entity.user_entity import UserProfileEntity


class UserProfileModel(db.Model):
    __tablename__ = "user_profiles"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    user_id = Column(BigInteger, ForeignKey(UserModel.id), nullable=False, unique=True)
    nickname = Column(String(12), nullable=True)
    last_update_code = Column(SmallInteger, nullable=True)
    survey_step = Column(SmallInteger, nullable=True)
    created_at = Column(DateTime, default=get_server_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=get_server_timestamp(), nullable=False)

    user_infos = relationship(
        "UserInfoModel", backref=backref("user_profiles"), uselist=True
    )
    survey_results = relationship(
        "SurveyResultModel",
        backref=backref("user_profiles"),
        uselist=True,
        primaryjoin="foreign(UserProfileModel.user_id)== SurveyResultModel.user_id",
        viewonly=True,
    )

    def to_entity(self) -> UserProfileEntity:
        return UserProfileEntity(
            id=self.id,
            user_id=self.user_id,
            nickname=self.nickname,
            last_update_code=self.last_update_code,
            survey_step=self.survey_step,
            created_at=self.created_at,
            updated_at=self.updated_at,
            user_infos=[
                user_info.to_result_entity()
                for user_info in self.user_infos
            ]
            if self.user_infos
            else None,
            survey_results=[
                survey_result.to_entity()
                for survey_result in self.survey_results
            ]
            if self.survey_results
            else None,
        )
