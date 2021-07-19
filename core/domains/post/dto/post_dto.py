from pydantic import BaseModel


class GetPostListDto(BaseModel):
    user_id: int
    post_category: int
    previous_post_id: int = None


class UpdatePostReadCountDto(BaseModel):
    user_id: int
    post_id: int
