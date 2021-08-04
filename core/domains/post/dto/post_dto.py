from pydantic import BaseModel


class GetPostListDto(BaseModel):
    post_category: int
    post_category_detail: int


class UpdatePostReadCountDto(BaseModel):
    post_id: int
