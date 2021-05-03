import random

import factory
from faker import Factory as FakerFactory

from app.persistence.model import InterestRegionModel
from app.persistence.model.user_model import UserModel

# factory에 사용해야 하는 Model을 가져온다
faker = FakerFactory.create(locale="ko_KR")


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
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


class InterestRegionFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = InterestRegionModel

    user_id = 1
    region_id = faker.random_digit()
