from sqlalchemy import Column, BigInteger, Integer, Boolean, DateTime

from app import db
from app.extensions.utils.time_helper import get_server_timestamp


class AppAgreeTermsModel(db.Model):
    __tablename__ = "app_agree_terms"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    user_id = Column(BigInteger, nullable=False, index=True)
    private_user_info_yn = Column(Boolean, nullable=False)
    required_terms_yn = Column(Boolean, nullable=False)
    receive_marketing_yn = Column(Boolean, nullable=False)
    receive_marketing_date = Column(DateTime, nullable=True)
    created_at = Column(
        DateTime(timezone=True), default=get_server_timestamp(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), default=get_server_timestamp(), nullable=False
    )
