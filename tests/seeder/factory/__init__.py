import uuid
from datetime import datetime

import factory
from faker import Factory as FakerFactory

from app.persistence.model import (
    InterestRegionModel,
    InterestRegionGroupModel,
    DeviceModel,
    DeviceTokenModel,
    UserProfileModel, AvgMonthlyIncomeWokrerModel, SidoCodeModel, NotificationModel
)
from app.persistence.model.user_model import UserModel

# factory에 사용해야 하는 Model을 가져온다
from core.domains.notification.enum.notification_enum import NotificationTopicEnum, NotificationBadgeTypeEnum, \
    NotificationStatusEnum

faker = FakerFactory.create(locale="ko_KR")


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta(object):
        abstract = True


class InterestRegionFactory(BaseFactory):
    class Meta:
        model = InterestRegionModel

    region_id = factory.Sequence(lambda n: n + 1)


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


class UserFactory(BaseFactory):
    """
    Define user factory
    """

    class Meta:
        model = UserModel

    is_required_agree_terms = True
    is_active = True
    is_out = False

    # interest_regions = factory.List([factory.SubFactory(InterestRegionFactory)])
    # devices = factory.List([factory.SubFactory(DeviceFactory)])
    interest_regions = factory.SubFactory(InterestRegionFactory)
    devices = factory.SubFactory(DeviceFactory)
    user_profiles = factory.SubFactory(UserProfileFactory)


class InterestRegionGroupFactory(BaseFactory):
    class Meta:
        model = InterestRegionGroupModel

    level = 2
    name = faker.city()
    interest_count = 0


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
    created_at = datetime.now().strptime("20210701", "%Y%m%d")
