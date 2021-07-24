import random
import uuid
from datetime import datetime

import factory
from faker import Factory as FakerFactory

from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model import (
    DeviceModel,
    DeviceTokenModel,
    UserProfileModel,
    AvgMonthlyIncomeWokrerModel,
    SidoCodeModel,
    NotificationModel,
    InterestHouseModel,
    ReceivePushTypeModel,
    AppAgreeTermsModel,
    PointTypeModel,
    PointModel,
    UserModel,
    ArticleModel,
    PostModel,
    PrivateSaleDetailModel,
    PrivateSaleModel,
    PublicSaleModel,
    RealEstateModel,
    RecentlyViewModel
)
# factory에 사용해야 하는 Model을 가져온다
from core.domains.house.enum.house_enum import HouseTypeEnum, RealTradeTypeEnum, BuildTypeEnum
from core.domains.notification.enum.notification_enum import NotificationTopicEnum, NotificationBadgeTypeEnum, \
    NotificationStatusEnum
from core.domains.post.enum.post_enum import PostTypeEnum, PostCategoryEnum
from core.domains.user.enum.user_enum import UserPointTypeDivisionEnum, UserPointCreatedByEnum, UserPointSignEnum

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
    endpoint = ""

    device_token = factory.SubFactory(DeviceTokenFactory)


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


class InterestHouseFactory(BaseFactory):
    class Meta:
        model = InterestHouseModel

    user_id = 1
    house_id = 1
    type = HouseTypeEnum.PUBLIC_SALES.value
    is_like = True


class PointTypeFactory(BaseFactory):
    class Meta:
        model = PointTypeModel

    name = "결제포인트 적립"
    division = UserPointTypeDivisionEnum.CHARGED.value


class PointFactory(BaseFactory):
    class Meta:
        model = PointModel

    amount = 1000
    sign = UserPointSignEnum.PLUS.value
    created_by = UserPointCreatedByEnum.SYSTEM.value
    created_at = get_server_timestamp()

    point_type = factory.SubFactory(PointTypeFactory)


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

    @factory.post_generation
    def device(obj, create, extracted, **kwargs):
        if extracted:
            DeviceFactory(users=obj, **kwargs)

    @factory.post_generation
    def user_profile(obj, create, extracted, **kwargs):
        if extracted:
            UserProfileFactory(users=obj, **kwargs)

    @factory.post_generation
    def receive_push_type(obj, create, extracted, **kwargs):
        if extracted:
            ReceivePushTypeFactory(users=obj, **kwargs)

    @factory.post_generation
    def interest_houses(obj, create, extracted, **kwargs):
        if extracted:
            InterestHouseFactory(users=obj, **kwargs)

    @factory.post_generation
    def point(obj, create, extracted, **kwargs):
        if extracted:
            PointFactory(users=obj, **kwargs)


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


class AppAgreeTermsFactory(BaseFactory):
    class Meta:
        model = AppAgreeTermsModel

    user_id = 1
    private_user_info_yn = True
    required_terms_yn = True
    receive_marketing_yn = True
    receive_marketing_date = get_server_timestamp()


class PostFactory(BaseFactory):
    class Meta:
        model = PostModel

    user_id = 1
    title = "떡볶이 나눠 먹어요"
    type = PostTypeEnum.ARTICLE.value
    is_deleted = False
    read_count = 0
    category_id = PostCategoryEnum.NOTICE.value
    created_at = get_server_timestamp()
    updated_at = get_server_timestamp()

    @factory.post_generation
    def Article(obj, create, extracted, **kwargs):
        if extracted:
            ArticleFactory(post=obj, **kwargs)


class ArticleFactory(BaseFactory):
    class Meta:
        model = ArticleModel

    post_id = 1
    body = factory.Sequence(lambda n: "body_게시글 입니다:) {}".format(n + 1))


class PrivateSaleDetailFactory(BaseFactory):
    class Meta:
        model = PrivateSaleDetailModel

    private_sales_id = factory.Sequence(lambda n: n + 1)
    private_area = random.uniform(40, 90)
    supply_area = random.uniform(50, 130)
    contract_date = "20210701"
    deposit_price = 0
    rent_price = 0
    trade_price = random.randint(10000, 50000)
    floor = random.randint(1, 20)
    trade_type = RealTradeTypeEnum.TRADING.value
    is_available = True


class PrivateSaleFactory(BaseFactory):
    class Meta:
        model = PrivateSaleModel

    real_estate_id = factory.Sequence(lambda n: n + 1)
    name = factory.Sequence(lambda n: f"아파트_{n}")
    building_type = BuildTypeEnum.APARTMENT.value
    private_sale_details = factory.List([factory.SubFactory(PrivateSaleDetailFactory)])


class PublicSaleDetailPhotoFactory(BaseFactory):
    pass


class PublicSaleDetailFactory(BaseFactory):
    pass


class PublicSalePhotoFactory(BaseFactory):
    pass


class PublicSaleFactory(BaseFactory):
    class Meta:
        model = PublicSaleModel


class RealEstateFactory(BaseFactory):
    class Meta:
        model = RealEstateModel

    name = faker.building_name()
    road_address = faker.road_address()
    jibun_address = faker.land_address()
    si_do = faker.province()
    si_gun_gu = faker.city() + faker.borough()
    dong_myun = "XX동"
    ri = "-"
    road_name = faker.road()
    road_number = faker.road_number() + faker.road_suffix()
    land_number = faker.land_number()
    is_available = True
    coordinates = f"SRID=4326;POINT({random.uniform(125.0666666, 131.8722222)} {random.uniform(33.1, 38.45)})"
    private_sales = factory.SubFactory(PrivateSaleFactory)
    public_sales = None


class RecentlyViewFactory(BaseFactory):
    class Meta:
        model = RecentlyViewModel

    user_id = 1
    house_id = 1
    type = HouseTypeEnum.PUBLIC_SALES.value
    created_at = get_server_timestamp()
