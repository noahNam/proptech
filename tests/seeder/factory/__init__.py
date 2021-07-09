import uuid
from datetime import datetime

import factory
from faker import Factory as FakerFactory

from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model import (
    DeviceModel,
    DeviceTokenModel,
    UserProfileModel, AvgMonthlyIncomeWokrerModel, SidoCodeModel, NotificationModel, InterestHouseModel,
    ReceivePushTypeModel, AppAgreeTermsModel
)
from app.persistence.model.user_model import UserModel

# factory에 사용해야 하는 Model을 가져온다
from core.domains.house.enum.house_enum import HouseTypeEnum
from core.domains.notification.enum.notification_enum import NotificationTopicEnum, NotificationBadgeTypeEnum, \
    NotificationStatusEnum

faker = FakerFactory.create(locale="ko_KR")


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta(object):
        abstract = True


class DeviceTokenFactory(BaseFactory):
    class Meta:
        model = DeviceTokenModel

    token = str(uuid.uuid4())


class DeviceFactory(BaseFactory):
    class Meta:
        model = DeviceModel

    uuid = str(uuid.uuid4())
    os = "AOS"
    is_active = True
    is_auth = True
    phone_number = "01012345678"

    # device_tokens = factory.List([factory.SubFactory(DeviceTokenFactory)])
    device_tokens = factory.SubFactory(DeviceTokenFactory)


class UserProfileFactory(BaseFactory):
    class Meta:
        model = UserProfileModel

    nickname = "noah"
    last_update_code = 1000


class ReceivePushTypeFactory(BaseFactory):
    class Meta:
        model = ReceivePushTypeModel

    is_official = True
    is_private = True
    is_marketing = True
    updated_at = datetime.now().strptime("20210701", "%Y%m%d")


class UserFactory(BaseFactory):
    """
    Define user factory
    """

    class Meta:
        model = UserModel

    is_required_agree_terms = True
    join_date = get_server_timestamp().strftime("%y%m%d")
    is_active = True
    is_out = False

    # devices = factory.List([factory.SubFactory(DeviceFactory)])
    devices = factory.SubFactory(DeviceFactory)
    user_profiles = factory.SubFactory(UserProfileFactory)
    receive_push_types = factory.SubFactory(ReceivePushTypeFactory)


class AvgMonthlyIncomeWorkerFactory(BaseFactory):
    class Meta:
        model = AvgMonthlyIncomeWokrerModel

    year = "2020"
    three = 6030160
    four = 7094205
    five = 7094205
    six = 7393647
    seven = 7778023
    eight = 8162399
    is_active = True


class SidoCodeFactory(BaseFactory):
    class Meta:
        model = SidoCodeModel

    sido_code = 11
    sido_name = "서울특별시"
    sigugun_code = 11010
    sigugun_name = "종로구"


class NotificationFactory(BaseFactory):
    class Meta:
        model = NotificationModel

    user_id = 1
    token = "device-token"
    endpoint = "application-platform-endpoint"
    topic = NotificationTopicEnum.SUB_NEWS.value
    badge_type = NotificationBadgeTypeEnum.ALL.value
    message = {}
    is_read = False
    is_pending = False
    status = NotificationStatusEnum.WAIT.value
    created_at = get_server_timestamp()


class InterestHouseFactory(BaseFactory):
    class Meta:
        model = InterestHouseModel

    user_id = 1
    house_id = 1
    type = HouseTypeEnum.PUBLIC_SALES.value
    is_like = True


class AppAgreeTermsFactory(BaseFactory):
    class Meta:
        model = AppAgreeTermsModel

    user_id = 1
    private_user_info_yn = True
    required_terms_yn = True
    receive_marketing_yn = True
    receive_marketing_date = get_server_timestamp()
