from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    DateTime,
    func,
    Boolean,
    JSON,
)
from app import db


from core.domains.house.entity.house_entity import SyncFailureHistoryEntity


class SyncFailureHistoryModel(db.Model):
    __tablename__ = "sync_failure_histories"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False,
    )
    target_table = Column(String(50), nullable=False)
    sync_data = Column(JSON(), nullable=False)
    is_solved = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def to_entity(self) -> SyncFailureHistoryEntity:
        return SyncFailureHistoryEntity(
            id=self.id,
            target_table=self.target_table,
            sync_data=self.sync_data,
            is_solved=self.is_solved,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
