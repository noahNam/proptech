from datetime import date

from sqlalchemy import and_, func, or_

from app.extensions.database import session
from app.extensions.utils.log_helper import logger_
from app.extensions.utils.time_helper import get_month_from_today
from app.persistence.model import RealEstateModel, PrivateSaleModel, PublicSaleModel, PublicSaleDetailModel, \
    PublicSalePhotoModel
from core.domains.house.dto.house_dto import CoordinatesRangeDto, RealEstateDto

logger = logger_.getLogger(__name__)


class HouseRepository:
    def get_queryset_by_coordinates_range_dto(self, dto: CoordinatesRangeDto):
        query = (
            # PrivateSale : 불러온 1달 이내 자료에서 평균값 -> 전세의 경우 rent_type=전세인 항목만 골라서 평균 (미완료)
            # PublicSale : 불러온 자료 내 Detail 테이블 평균 -> (미완료)
            # Query list -> pydantic 모델화 (validation 문제로 변경 힘듬)
            # 추가되어야할 column : 취득세 최소 - 최대, 행정구역 - short_name
            session.query(RealEstateModel)
                .join(RealEstateModel.private_sales, isouter=True)
                .join(RealEstateModel.public_sales, isouter=True)
                .join(PublicSaleModel.public_sale_details, isouter=True)
                .join(PublicSaleModel.public_sale_photos, isouter=True)
                .with_entities(RealEstateModel,
                               func.ST_Y(RealEstateModel.coordinates).label("latitude"),
                               func.ST_X(RealEstateModel.coordinates).label("longitude"),
                               PrivateSaleModel,
                               PublicSaleModel,
                               PublicSalePhotoModel,
                               PublicSaleDetailModel)
                .filter(or_(and_(RealEstateModel.is_available == "True",
                                 PrivateSaleModel.is_available == "True",
                                 PrivateSaleModel.contract_date >= get_month_from_today(),
                                 PrivateSaleModel.contract_date <= date.today()),
                            and_(RealEstateModel.is_available == "True",
                                 PublicSaleModel.is_available == "True"),
                            and_(RealEstateModel.is_available == "True",
                                 PrivateSaleModel.is_available == "True",
                                 PublicSaleModel.is_available == "True",
                                 PrivateSaleModel.contract_date >= get_month_from_today(),
                                 PrivateSaleModel.contract_date <= date.today())))
                .filter(func.ST_Contains(func.ST_MakeEnvelope(dto.start_x, dto.end_y, dto.end_x, dto.start_y, 4326),
                                         RealEstateModel.coordinates))

        )
        queryset = query.all()

        return queryset

    def get_real_estates_from_queryset(self, queryset: list):
        if not queryset:
            return None

        estate_private_list = []
        estate_public_list = []
        private_sale_entity_list = []
        public_sale_entity_list = []
        public_sale_photo_list = []
        public_sale_detail_entity_list = []

        # Make Entity
        for query in queryset:
            real_estate = query[0]
            lat = query[1]
            lon = query[2]
            private_sale = query[3]
            public_sale = query[4]
            public_sale_photo = query[5]
            public_sale_detail = query[6]

            if real_estate and lat and lon and private_sale:
                if not estate_private_list:
                    estate_private_list.append(real_estate.to_entity(lat, lon))
                else:
                    # real_estate 중복 pk pass
                    for entry in private_sale_entity_list:
                        if entry.id != real_estate.id:
                            estate_private_list.append(real_estate.to_entity(lat, lon))
                        else:
                            continue
                private_sale_entity_list.append(private_sale.to_entity())
            elif real_estate and lat and lon and public_sale:
                if not public_sale_detail_entity_list:
                    estate_public_list.append(real_estate.to_entity(lat, lon))
                    public_sale_entity_list.append(public_sale.to_entity())
                    public_sale_photo_list.append(public_sale_photo.to_entity())
                else:
                    # real_estate 중복 pk pass
                    # public_sale 중복 pk pass
                    # public_sale_photo 중복 pk pass
                    for entry in public_sale_detail_entity_list:
                        if entry.id != public_sale.id:
                            estate_public_list.append(real_estate.to_entity(lat, lon))
                            public_sale_entity_list.append(public_sale.to_entity())
                            public_sale_photo_list.append(public_sale_photo.to_entity())
                        else:
                            continue
                public_sale_detail_entity_list.append(public_sale_detail.to_entity())
            else:
                # Unexpected error
                continue

            print('------------')
            print(estate_private_list)
            print(estate_public_list)
            print(public_sale_entity_list)
            print(public_sale_photo_list)
            print(public_sale_detail_entity_list)


        return
