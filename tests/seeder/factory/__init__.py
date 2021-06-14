import random
import uuid

import factory
from faker import Factory as FakerFactory

from app.persistence.model import InterestRegionModel, InterestRegionGroupModel, DeviceModel, DeviceTokenModel
from app.persistence.model.user_model import UserModel

# factory에 사용해야 하는 Model을 가져온다
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

    os = "AOS"
    is_active = True
    is_auth = False
    phone_number = None

    device_tokens = factory.List([factory.SubFactory(DeviceTokenFactory)])


class UserFactory(BaseFactory):
    """
    Define user factory
    """

    class Meta:
        model = UserModel

    nickname = faker.name()
    email = faker.email()
    gender = random.choice("FM")
    birthday = faker.date_of_birth().strftime("%Y%m%d")
    is_active = True
    is_out = False
    profile_img_id = 1

    interest_regions = factory.List([factory.SubFactory(InterestRegionFactory)])
    devices = factory.List([factory.SubFactory(DeviceFactory)])


class InterestRegionGroupFactory(BaseFactory):
    class Meta:
        model = InterestRegionGroupModel

    name = faker.city()
    interest_count = 0
