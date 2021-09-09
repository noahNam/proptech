from pydantic import BaseModel


class GetPostListDto(BaseModel):
    post_category: int
    post_category_detail: int
    previous_post_id: int = None


class UpdatePostReadCountDto(BaseModel):
    post_id: int
