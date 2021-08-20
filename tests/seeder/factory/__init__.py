import random
import uuid
from datetime import datetime

import factory
from faker import Factory as FakerFactory
from strgen import StringGenerator

from app.extensions.utils.time_helper import (
    get_server_timestamp,
    get_random_date_about_one_month_from_today,
)
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
    TicketTypeModel,
    TicketModel,
    UserModel,
    ArticleModel,
    PostModel,
    PrivateSaleDetailModel,
    PrivateSaleModel,
    PublicSaleModel,
    RealEstateModel,
    RecentlyViewModel,
    PublicSaleDetailPhotoModel,
    PublicSaleDetailModel,
    PublicSalePhotoModel,
    AdministrativeDivisionModel,
    SurveyResultModel,
    UserInfoModel,
    TicketUsageResultModel,
    HouseTypeRankModel,
    PromotionModel,
    PromotionHouseModel,
    PromotionUsageCountModel,
    TicketTargetModel,
    PostAttachmentModel,
    RecommendCodeModel,
    BannerModel,
    BannerImageModel,
    ButtonLinkModel,
)
from core.domains.house.enum.house_enum import (
    HouseTypeEnum,
    RealTradeTypeEnum,
    BuildTypeEnum,
    HousingCategoryEnum,
    RentTypeEnum,
    PreSaleTypeEnum,
    DivisionLevelEnum,
    SectionType,
    BannerSubTopic,
)
from core.domains.notification.enum.notification_enum import (
    NotificationTopicEnum,
    NotificationBadgeTypeEnum,
    NotificationStatusEnum,
)
from core.domains.payment.enum.payment_enum import TicketSignEnum, PromotionTypeEnum
from core.domains.post.enum.post_enum import (
    PostCategoryEnum,
    PostCategoryDetailEnum,
)
from core.domains.user.enum.user_enum import (
    UserTicketTypeDivisionEnum,
    UserTicketCreatedByEnum,
)

# factory에 사용해야 하는 Model을 가져온다

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


class SurveyResultFactory(BaseFactory):
    class Meta:
        model = SurveyResultModel

    user_id = 1
    total_point = 32
    detail_point_house = 24
    detail_point_family = 25
    detail_point_bank = 26
    public_newly_married = 10
    public_newly_married_div = "우선"
    public_first_life = 11
    public_first_life_div = "잔여"
    public_multiple_children = 12
    public_old_parent = 13
    public_agency_recommend = 14
    public_normal = 15
    private_newly_married = 16
    private_newly_married_div = "잔여"
    private_first_life = 17
    private_first_life_div = "우선"
    private_old_parent = 19
    private_agency_recommend = 20
    private_normal = 21
    hope_town_phase_one = 7
    hope_town_phase_two = 9
    created_at = get_server_timestamp()
    updated_at = get_server_timestamp()


class UserInfoFactory(BaseFactory):
    class Meta:
        model = UserInfoModel

    code = 1001
    value = "19850509"


class UserProfileFactory(BaseFactory):
    class Meta:
        model = UserProfileModel

    nickname = "noah"
    last_update_code = 1000
    survey_step = 1

    user_infos = factory.List([factory.SubFactory(UserInfoFactory)])
    survey_result = factory.SubFactory(SurveyResultFactory)


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


class TicketTargetFactory(BaseFactory):
    class Meta:
        model = TicketTargetModel

    public_house_id = factory.Sequence(lambda n: n + 1)


class TicketTypeFactory(BaseFactory):
    class Meta:
        model = TicketTypeModel

    division = UserTicketTypeDivisionEnum.CHARGED.value


class TicketFactory(BaseFactory):
    class Meta:
        model = TicketModel

    type = 1
    amount = 1
    sign = TicketSignEnum.PLUS.value
    is_active = True
    created_by = UserTicketCreatedByEnum.SYSTEM.value
    created_at = get_server_timestamp()

    @factory.post_generation
    def ticket_type(obj, create, extracted, **kwargs):
        if extracted:
            TicketTypeFactory(users=obj, **kwargs)

    @factory.post_generation
    def ticket_targets(obj, create, extracted, **kwargs):
        if extracted:
            for _ in range(3):
                TicketTargetFactory(users=obj, **kwargs)


class HouseTypeRankFactory(BaseFactory):
    class Meta:
        model = HouseTypeRankModel

    ticket_usage_result_id = 1
    house_structure_type = factory.Sequence(lambda n: f"59B_{n}")
    subscription_type = factory.Sequence(lambda n: f"신혼부부_{n}")
    rank = factory.Sequence(lambda n: n + 1)


class TicketUsageResultFactory(BaseFactory):
    class Meta:
        model = TicketUsageResultModel

    user_id = 1
    public_house_id = 1
    ticket_id = None
    is_active = True
    created_at = get_server_timestamp()

    house_type_ranks = factory.List([factory.SubFactory(HouseTypeRankFactory)])


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
    number_ticket = 0

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
    def tickets(obj, create, extracted, **kwargs):
        if extracted:
            TicketFactory(users=obj, **kwargs)

    @factory.post_generation
    def recently_view(obj, create, extracted, **kwargs):
        if extracted:
            RecentlyViewFactory(users=obj, **kwargs)


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


class ArticleFactory(BaseFactory):
    class Meta:
        model = ArticleModel

    post_id = 1
    body = factory.Sequence(lambda n: "body_게시글 입니다:) {}".format(n + 1))
    created_at = get_server_timestamp()
    updated_at = get_server_timestamp()


class PostAttachmentFactory(BaseFactory):
    class Meta:
        model = PostAttachmentModel

    post_id = 1
    file_name = "photo_file"
    path = "public_sale_detail_photos/2021/790bd67d-0865-4f61-95a7-12cadba916b5.jpeg"
    extension = "jpeg"
    type = 0
    created_at = get_server_timestamp()
    updated_at = get_server_timestamp()


class PostFactory(BaseFactory):
    class Meta:
        model = PostModel

    title = "회원가입 관련 안내사항"
    desc = "회원 가입 기준은?"
    is_deleted = False
    read_count = 0
    category_id = PostCategoryEnum.NOTICE.value
    category_detail_id = PostCategoryDetailEnum.NO_DETAIL.value
    contents_num = factory.Sequence(lambda n: n + 1)
    created_at = get_server_timestamp()
    updated_at = get_server_timestamp()

    @factory.post_generation
    def article(obj, create, extracted, **kwargs):
        if extracted:
            ArticleFactory(post=obj, **kwargs)

    @factory.post_generation
    def post_attachments(obj, create, extracted, **kwargs):
        if extracted:
            PostAttachmentFactory(post=obj, **kwargs)


class PrivateSaleDetailFactory(BaseFactory):
    class Meta:
        model = PrivateSaleDetailModel

    private_sales_id = 1
    private_area = random.uniform(40, 90)
    supply_area = random.uniform(50, 130)
    contract_date = get_random_date_about_one_month_from_today().strftime("%Y%m%d")
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
    created_at = get_server_timestamp()
    updated_at = get_server_timestamp()

    @factory.post_generation
    def private_sale_details(obj, create, extracted, **kwargs):
        if extracted:
            PrivateSaleDetailFactory(private_sales=obj, **kwargs)


class PublicSaleDetailPhotoFactory(BaseFactory):
    class Meta:
        model = PublicSaleDetailPhotoModel

    public_sale_details_id = factory.Sequence(lambda n: n + 1)
    file_name = "photo_file"
    path = "public_sale_detail_photos/2021/790bd67d-0865-4f61-95a7-12cadba916b5.jpeg"
    extension = "jpeg"
    created_at = get_server_timestamp()
    updated_at = get_server_timestamp()


class PublicSaleDetailFactory(BaseFactory):
    class Meta:
        model = PublicSaleDetailModel

    public_sales_id = 1
    private_area = random.uniform(40, 90)
    supply_area = random.uniform(50, 130)
    supply_price = random.randint(10000, 50000)
    acquisition_tax = random.randint(1000000, 5000000)

    @factory.post_generation
    def private_sale_detail_photos(obj, create, extracted, **kwargs):
        if extracted:
            PublicSaleDetailPhotoFactory(public_sale_details=obj, **kwargs)


class PublicSalePhotoFactory(BaseFactory):
    class Meta:
        model = PublicSalePhotoModel

    public_sales_id = factory.Sequence(lambda n: n + 1)
    file_name = "photo_file"
    path = "public_sale_detail_photos/2021/790bd67d-0865-4f61-95a7-12cadba916b5.jpeg"
    extension = "jpeg"
    created_at = get_server_timestamp()
    updated_at = get_server_timestamp()


class PublicSaleFactory(BaseFactory):
    class Meta:
        model = PublicSaleModel

    real_estate_id = factory.Sequence(lambda n: n + 1)
    name = factory.Sequence(lambda n: f"아파트_{n}")
    name_ts = factory.Sequence(lambda n: f"아파트_{n}")
    region = "경기"
    housing_category = HousingCategoryEnum.PUBLIC.value
    rent_type = RentTypeEnum.PRE_SALE.value
    trade_type = PreSaleTypeEnum.PRE_SALE.value
    construct_company = "건설회사"
    supply_household = random.randint(100, 500)
    is_available = True
    offer_date = get_random_date_about_one_month_from_today().strftime("%Y%m%d")
    subscription_start_date = get_random_date_about_one_month_from_today().strftime(
        "%Y%m%d"
    )
    subscription_end_date = get_random_date_about_one_month_from_today().strftime(
        "%Y%m%d"
    )
    special_supply_date = get_random_date_about_one_month_from_today().strftime(
        "%Y%m%d"
    )
    special_supply_etc_date = get_random_date_about_one_month_from_today().strftime(
        "%Y%m%d"
    )
    first_supply_date = get_random_date_about_one_month_from_today().strftime("%Y%m%d")
    first_supply_etc_date = get_random_date_about_one_month_from_today().strftime(
        "%Y%m%d"
    )
    second_supply_date = get_random_date_about_one_month_from_today().strftime("%Y%m%d")
    second_supply_etc_date = get_random_date_about_one_month_from_today().strftime(
        "%Y%m%d"
    )
    notice_winner_date = get_random_date_about_one_month_from_today().strftime("%Y%m%d")
    contract_start_date = get_random_date_about_one_month_from_today().strftime(
        "%Y%m%d"
    )
    contract_end_date = get_random_date_about_one_month_from_today().strftime("%Y%m%d")
    move_in_year = random.randint(2023, 2025)
    move_in_month = random.randint(1, 12)
    min_down_payment = random.randint(10_000_000, 50_000_000)
    max_down_payment = random.randint(10_000_000, 50_000_000)
    down_payment_ratio = 20
    reference_url = "https://www.reference.com"
    created_at = get_server_timestamp()
    updated_at = get_server_timestamp()

    @factory.post_generation
    def private_sale_photos(obj, create, extracted, **kwargs):
        if extracted:
            PublicSalePhotoFactory(public_sales=obj, **kwargs)

    @factory.post_generation
    def private_sale_details(obj, create, extracted, **kwargs):
        if extracted:
            PublicSaleDetailFactory(public_sales=obj, **kwargs)


class RealEstateFactory(BaseFactory):
    class Meta:
        model = RealEstateModel

    name = faker.building_name()
    road_address = faker.road_address()
    jibun_address = faker.land_address()
    road_address_ts = faker.land_address()
    jibun_address_ts = faker.land_address()
    si_do = faker.province()
    si_gun_gu = faker.city() + faker.borough()
    dong_myun = "XX동"
    ri = "-"
    road_name = faker.road()
    road_number = faker.road_number() + faker.road_suffix()
    land_number = faker.land_number()
    is_available = True
    coordinates = f"SRID=4326;POINT({random.uniform(125.0666666, 131.8722222)} {random.uniform(33.1, 38.45)})"

    latitude = random.uniform(33.1, 38.45)
    longitude = random.uniform(125.0666666, 131.8722222)

    @factory.post_generation
    def private_sales(obj, create, extracted, **kwargs):
        if extracted:
            PrivateSaleFactory(real_estates=obj, **kwargs)

    @factory.post_generation
    def public_sales(obj, create, extracted, **kwargs):
        if extracted:
            PublicSaleFactory(real_estates=obj, **kwargs)


class RecentlyViewFactory(BaseFactory):
    class Meta:
        model = RecentlyViewModel

    user_id = 1
    house_id = 1
    type = HouseTypeEnum.PUBLIC_SALES.value
    created_at = get_server_timestamp()


class AdministrativeDivisionFactory(BaseFactory):
    class Meta:
        model = AdministrativeDivisionModel

    name = factory.Sequence(lambda n: f"XX시 XX구 읍면동_{n}")
    name_ts = factory.Sequence(lambda n: f"XX시 XX구 읍면동_{n}")
    short_name = factory.Sequence(lambda n: f"읍면동_{n}")
    real_trade_price = random.randint(10_000_000, 50_000_000)
    real_rent_price = random.randint(10_000_000, 50_000_000)
    real_deposit_price = random.randint(10_000_000, 50_000_000)
    public_sale_price = random.randint(10_000_000, 50_000_000)
    level = DivisionLevelEnum.LEVEL_3.value
    coordinates = f"SRID=4326;POINT({random.uniform(125.0666666, 131.8722222)} {random.uniform(33.1, 38.45)})"

    latitude = random.uniform(33.1, 38.45)
    longitude = random.uniform(125.0666666, 131.8722222)
    created_at = get_server_timestamp()
    updated_at = get_server_timestamp()


class PromotionHouseFactory(BaseFactory):
    class Meta:
        model = PromotionHouseModel

    house_id = factory.Sequence(lambda n: n + 1)


class PromotionUsageCountFactory(BaseFactory):
    class Meta:
        model = PromotionUsageCountModel

    user_id = 1
    usage_count = 1


class PromotionFactory(BaseFactory):
    class Meta:
        model = PromotionModel

    type = PromotionTypeEnum.ALL.value
    max_count = 1
    is_active = True
    created_at = get_server_timestamp()
    updated_at = get_server_timestamp()

    @factory.post_generation
    def promotion_houses(obj, create, extracted, **kwargs):
        if extracted:
            for _ in range(3):
                PromotionHouseFactory(promotions=obj, **kwargs)

    @factory.post_generation
    def promotion_usage_count(obj, create, extracted, **kwargs):
        if extracted:
            PromotionUsageCountFactory(promotions=obj, **kwargs)


class RecommendCodeFactory(BaseFactory):
    class Meta:
        model = RecommendCodeModel

    user_id = 1
    code_group = int(user_id / 1000)
    code = (StringGenerator("[\l]{6}").render_list(1, unique=True)[0]).upper()
    code_count = 0
    is_used = False


class BannerImageFactory(BaseFactory):
    class Meta:
        model = BannerImageModel

    banner_id = factory.Sequence(lambda n: n + 1)
    file_name = "photo_file"
    path = "public_sale_detail_photos/2021/790bd67d-0865-4f61-95a7-12cadba916b5.jpeg"
    extension = "jpeg"
    created_at = get_server_timestamp()
    updated_at = get_server_timestamp()


class BannerFactory(BaseFactory):
    class Meta:
        model = BannerModel

    title = factory.Sequence(lambda n: f"배너_{n}")
    desc = factory.Sequence(lambda n: f"배너설명_{n}")
    section_type = SectionType.HOME_SCREEN.value
    sub_topic = BannerSubTopic.HOME_SUBSCRIPTION_BY_REGION.value
    contents_num = factory.Sequence(lambda n: n + 1)
    reference_url = "https://www.reference.com"
    is_active = True
    is_event = True

    @factory.post_generation
    def banner_image(obj, create, extracted, **kwargs):
        if extracted:
            BannerImageFactory(banner=obj, **kwargs)


class ButtonLinkFactory(BaseFactory):
    class Meta:
        model = ButtonLinkModel

    title = factory.Sequence(lambda n: f"버튼_{n}")
    reference_url = "https://www.reference.com"
    section_type = SectionType.HOME_SCREEN.value
    is_active = True
