from typing import List, Union
from app.extensions.database import session
from app.extensions.utils.log_helper import logger_
from app.persistence.model.post_model import PostModel
from core.domains.post.dto.post_dto import GetPostListDto
from core.domains.post.entity.post_entity import PostEntity
from core.domains.post.enum.post_enum import PostLimitEnum

logger = logger_.getLogger(__name__)


class PostRepository:
    def is_post_exist(self, post_id: int) -> bool:
        return session.query(
            session.query(PostModel).filter_by(id=post_id).exists()
        ).scalar()

    def get_post_list_include_article(
            self,
            dto: GetPostListDto
    ) -> Union[List[PostEntity], List]:
        search_filter = list()
        search_filter.append(PostModel.is_deleted == False)
        search_filter.append(PostModel.category_id == dto.post_category)

        previous_post_id_filter = list()
        if dto.previous_post_id:
            previous_post_id_filter.append(PostModel.id < dto.previous_post_id)

        try:
            query = (
                session.query(PostModel).filter(
                    *search_filter,
                    *previous_post_id_filter,
                )
            )

            post_list = (
                query.order_by(PostModel.id.desc())
                    .limit(PostLimitEnum.LIMIT.value)
                    .all()
            )

            return [post.to_entity() for post in post_list]
        except Exception as e:
            logger.error(f"[PostRepository][get_post_list_include_article] error : {e}")
            return []

    def update_read_count(self, post_id: int) -> None:
        try:
            session.query(PostModel).filter_by(id=post_id).update(
                {"read_count": PostModel.read_count + 1}
            )
        except Exception as e:
            logger.error(
                f"[PostRepository][update_read_count] post_id : {post_id} error : {e}"
            )
            session.rollback()
