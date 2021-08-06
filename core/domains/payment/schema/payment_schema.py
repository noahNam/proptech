from typing import List, Optional

from pydantic import BaseModel, StrictStr, StrictInt


class GetTicketUsageResultBaseSchema(BaseModel):
    house_id: StrictInt
    name: StrictStr
    image_path: Optional[StrictStr]


class UseBasicTicketBaseSchema(BaseModel):
    type: StrictStr
    message: StrictStr


class GetRecommendCodeBaseSchema(BaseModel):
    code: StrictStr


class GetTicketUsageResultResponseSchema(BaseModel):
    houses: List[GetTicketUsageResultBaseSchema]


class UseBasicTicketResponseSchema(BaseModel):
    ticket_usage_result: UseBasicTicketBaseSchema


class CreateRecommendCodeResponseSchema(BaseModel):
    recommend_code: StrictStr


class GetRecommendCodeResponseSchema(BaseModel):
    recommend_code: StrictStr


class UseRecommendCodeResponseSchema(BaseModel):
    result: StrictStr
