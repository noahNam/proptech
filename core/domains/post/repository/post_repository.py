from typing import List, Union

from sqlalchemy import and_

from app.extensions.database import session
from app.extensions.utils.log_helper import logger_
from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model import PostAttachmentModel
from app.persistence.model.post_model import PostModel
from core.domains.post.dto.post_dto import GetPostListDto
from core.domains.post.entity.post_entity import PostEntity, ArticleEntity
from core.domains.post.enum.post_enum import (
    PostLimitEnum,
    PostCategoryEnum,
    PostCategoryDetailEnum,
)

logger = logger_.getLogger(__name__)


class PostRepository:
    def is_post_exist(self, post_id: int) -> bool:
        return session.query(
            session.query(PostModel).filter_by(id=post_id).exists()
        ).scalar()

    def get_post_list_include_contents(
        self, dto: GetPostListDto
    ) -> Union[List[PostEntity], List]:
        search_filter = list()

        # FAQ, All_list
        if (
            dto.post_category == PostCategoryEnum.FAQ.value
            and dto.post_category_detail == PostCategoryDetailEnum.ALL_LIST.value
        ):
            search_filter.append(
                and_(
                    PostModel.is_deleted == False,
                    PostModel.category_id == dto.post_category,
                )
            )
        else:
            search_filter.append(
                and_(
                    PostModel.is_deleted == False,
                    PostModel.category_id == dto.post_category,
                    PostModel.category_detail_id == dto.post_category_detail,
                )
            )
        previous_post_id_filter = list()
        if dto.previous_post_id:
            previous_post_id_filter.append(PostModel.id < dto.previous_post_id)

        try:
            query = (
                session.query(PostModel)
                .join(PostModel.article, isouter=True)
                .join(PostModel.post_attachments, isouter=True)
                .filter(*search_filter)
                .filter(*previous_post_id_filter)
            )

            # 공지사항 포스트일경우 Pagination 적용
            if (
                dto.post_category == PostCategoryEnum.NOTICE.value
                and dto.post_category_detail == PostCategoryDetailEnum.NO_DETAIL.value
            ):
                post_list = (
                    query.order_by(PostModel.id.desc())
                    .limit(PostLimitEnum.LIMIT.value)
                    .all()
                )
            else:
                post_list = (
                    query.order_by(
                        PostModel.category_id.asc(),
                        PostModel.category_detail_id.asc(),
                        PostModel.contents_num.asc(),
                        PostAttachmentModel.id.asc()
                    )
                    .all()
                )
            return [post.to_entity() for post in post_list]
        except Exception as e:
            logger.error(
                f"[PostRepository][get_post_list_include_contents] error : {e}"
            )
            return []

    def update_read_count(self, post_id: int) -> None:
        try:
            session.query(PostModel).filter_by(id=post_id).update(
                {
                    "read_count": PostModel.read_count + 1,
                    "updated_at": get_server_timestamp(),
                }
            )
            session.commit()

        except Exception as e:
            logger.error(
                f"[PostRepository][update_read_count] post_id : {post_id} error : {e}"
            )
            session.rollback()
