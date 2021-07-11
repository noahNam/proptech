from pydantic import BaseModel


class GetPostListDto(BaseModel):
    post_category: int
    previous_post_id: int = None
