import random
import uuid

import factory
from faker import Factory as FakerFactory

from app.persistence.model import (
    InterestRegionModel,
    InterestRegionGroupModel,
    DeviceModel,
    DeviceTokenModel,
)
from app.persistence.model.user_model import UserModel

# factory에 사용해야 하는 Model을 가져온다
from core.domains.user.enum.user_enum import UserHomeOwnerType, UserInterestedHouseType

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

    device_tokens = factory.List([factory.SubFactory(DeviceTokenFactory)])


class UserFactory(BaseFactory):
    """
    Define user factory
    """

    class Meta:
        model = UserModel

    home_owner_type = random.choice(
        [UserHomeOwnerType.OWNER.value, UserHomeOwnerType.NOT_OWNER.value, UserHomeOwnerType.BEFORE_OWNER.value])
    interested_house_type = random.choice(
        [UserInterestedHouseType.SUBSCRIPTION.value, UserInterestedHouseType.RENT.value,
         UserInterestedHouseType.BUY_HOUSE.value])
    is_required_agree_terms = True
    is_active = True
    is_out = False

    interest_regions = factory.List([factory.SubFactory(InterestRegionFactory)])
    devices = factory.List([factory.SubFactory(DeviceFactory)])


class InterestRegionGroupFactory(BaseFactory):
    class Meta:
        model = InterestRegionGroupModel

    name = faker.city()
    interest_count = 0
