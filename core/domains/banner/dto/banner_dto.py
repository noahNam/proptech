from pydantic import BaseModel


class SectionTypeDto(BaseModel):
    section_type: int


class GetHomeBannerDto(BaseModel):
    section_type: int
    user_id: int
