from enum import Enum


class TopicEnum(Enum):
    PRE_PRCS_INTEREST_HOUSE = "tanos.pre_prcs_interest_house_data.v1"
    CONVERT_NOTICE_PUSH_MESSAGE = "tanos.convert_notice_push_message.v1"
    PRE_CALCULATE_AVERAGE_HOUSE = "tanos.pre_calculate_average_house_data.v1"
    ADD_LEGAL_CODE_HOUSE = "tanos.add_legal_code_house_data.v1"
    PRE_CALCULATE_AVERAGE_ADMINISTRATIVE = (
        "tanos.pre_calculate_average_administrative_data.v1"
    )
    INSERT_UPLOAD_PUBLIC_SALES_AND_DETAIL_IMAGE = (
        "tanos.insert_upload_public_sales_and_detail_image.v1"
    )
    REPLACE_PUBLIC_TO_PRIVATE_SALES = "tanos.replace_public_to_private_sales.v1"
