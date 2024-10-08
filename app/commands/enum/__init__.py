from enum import Enum


class TopicEnum(Enum):
    PRE_PRCS_INTEREST_HOUSE = "tanos.pre_prcs_interest_house_data.v1"
    CONVERT_NOTICE_PUSH_MESSAGE = "tanos.convert_notice_push_message.v1"
    ADD_LEGAL_CODE_HOUSE = "tanos.add_legal_code_house_data.v1"
    PRE_CALCULATE_AVERAGE_HOUSE = "tanos.pre_calculate_average_house_data.v1"
    PRE_CALCULATE_AVERAGE_ADMINISTRATIVE = (
        "tanos.pre_calculate_average_administrative_data.v1"
    )
    UPSERT_UPLOAD_PUBLIC_SALES_AND_DETAIL_IMAGE = (
        "tanos.upsert_upload_public_sales_and_detail_image.v1"
    )
    REPLACE_PUBLIC_TO_PRIVATE_SALES = "tanos.replace_public_to_private_sales.v1"
    CHECK_NOT_UPLOADED_PHOTOS = "tanos.check_not_uploaded_photos.v1"
    ADD_SUPPLY_AREA_TO_PRIVATE_SALE_DETAILS = (
        "tanos.add_supply_area_to_private_sale_details.v1"
    )
    BIND_SUPPLY_AREA_TO_PRIVATE_SALE_DETAILS = (
        "tanos.bind_supply_area_to_private_sale_details.v1"
    )

    # message pulling from redis
    SET_REDIS = "tanos.set_redis.v1"
    SYNC_HOUSE_DATA = "tanos.sync_house_data.v1"
