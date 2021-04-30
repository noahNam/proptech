from sqlalchemy import Column, BigInteger, Integer, String

from app import db
from core.domains.user.entity.user_entity import UserEntity
from core.domains.user.enum.user_enum import UserDefaultValueEnum


class UserModel(db.Model):
    __tablename__ = "users"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        nullable=False,
    )
    nickname = Column(String(20), nullable=False, default=UserDefaultValueEnum.NICKNAME.value)
    email = Column(String(40), nullable=False)
    nickname = Column(String(20), nullable=False)
    nickname = Column(String(20), nullable=False)
    nickname = Column(String(20), nullable=False)
    status = Column(String(10), nullable=True)
    sex = Column(String(1), nullable=True)

    def to_entity(self) -> UserEntity:
        return UserEntity(
            id=self.id,
            nickname=self.nickname,
            status=self.status,
            sex=self.sex
        )
