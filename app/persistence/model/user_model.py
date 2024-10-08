from sqlalchemy import (
    Column,
    BigInteger,
    Boolean,
    DateTime,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship, backref

from app import db
from core.domains.user.entity.user_entity import UserEntity, PushTargetEntity


class UserModel(db.Model):
    __tablename__ = "users"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    email = Column(String(75), nullable=True)
    is_required_agree_terms = Column(Boolean, nullable=False, default=False)
    join_date = Column(String(8), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_out = Column(Boolean, nullable=False, default=False)
    number_ticket = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    device = relationship("DeviceModel", backref=backref("users"), uselist=False)
    user_profile = relationship(
        "UserProfileModel", backref=backref("users"), uselist=False
    )
    receive_push_type = relationship(
        "ReceivePushTypeModel", backref=backref("users"), uselist=False
    )
    interest_houses = relationship(
        "InterestHouseModel", back_populates="users", uselist=True
    )
    tickets = relationship("TicketModel", backref=backref("users"), uselist=True)
    recently_views = relationship("RecentlyViewModel", back_populates="users")

    def to_entity(self) -> UserEntity:
        return UserEntity(
            id=self.id,
            email=self.email,
            is_required_agree_terms=self.is_required_agree_terms,
            join_date=self.join_date,
            is_active=self.is_active,
            is_out=self.is_out,
            number_ticket=self.number_ticket,
            device=self.device.to_entity(),
            user_profile=self.user_profile.to_entity() if self.user_profile else None,
            receive_push_type=self.receive_push_type.to_entity(),
            interest_houses=[
                interest_house.to_entity() for interest_house in self.interest_houses
            ]
            if self.interest_houses
            else None,
            tickets=[ticket.to_entity() for ticket in self.tickets]
            if self.tickets
            else None,
        )

    def to_push_target_entity(self) -> PushTargetEntity:
        return PushTargetEntity(
            id=self.id, is_active=self.is_active, device=self.device.to_entity(),
        )
