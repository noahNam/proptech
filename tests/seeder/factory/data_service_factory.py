import factory

from . import UserFactory, InterestRegionFactory


class NormalUserFactory(UserFactory):
    """
    일반 유저 생성기
    Todo 참조되는 모델 이곳에 추가
    """

    @factory.post_generation
    def interest_region(self, create, extracted, **kwargs):
        if extracted:
            InterestRegionFactory(**kwargs)
