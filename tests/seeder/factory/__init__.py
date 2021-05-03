import random

import factory
from factory import Sequence
from faker import Factory as FakerFactory

from app.persistence.model import InterestRegionModel
from app.persistence.model.user_model import UserModel

# factory에 사용해야 하는 Model을 가져온다
faker = FakerFactory.create(locale="ko_KR")


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta(object):
        abstract = True


class InterestRegionFactory(BaseFactory):
    class Meta:
        model = InterestRegionModel

    region_id = factory.Sequence(lambda n: n+1)


class UserFactory(BaseFactory):
    """
    Define user factory
    """

    class Meta:
        model = UserModel

    nickname = faker.name()
    email = faker.email()
    gender = random.choice('FM')
    birthday = faker.date_of_birth().strftime("%Y%m%d")
    is_active = True
    is_out = False
    profile_img_id = 1

    interest_regions = factory.List([factory.SubFactory(InterestRegionFactory)])
