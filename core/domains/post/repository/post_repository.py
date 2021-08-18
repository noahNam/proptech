from typing import List, Union

from sqlalchemy import and_

from app.extensions.database import session
from app.extensions.utils.log_helper import logger_
from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model import PostAttachmentModel
from app.persistence.model.post_model import PostModel
from core.domains.post.dto.post_dto import GetPostListDto
from core.domains.post.entity.post_entity import PostEntity, ArticleEntity

logger = logger_.getLogger(__name__)


class PostRepository:
    def is_post_exist(self, post_id: int) -> bool:
        return session.query(
            session.query(PostModel).filter_by(id=post_id).exists()
        ).scalar()

    def _get_article_entity(self, post_list: List[PostModel]) -> Union[List[ArticleEntity], List]:
        result = list()
        if not post_list:
            return []
        for post in post_list:
            body = post.article.body.split("\r\n")
            result.append(ArticleEntity(tokenized_body=body))
        return result

    def get_post_list_include_contents(
            self, dto: GetPostListDto
    ) -> Union[List[PostEntity], List]:
        search_filter = list()
        search_filter.append(
            and_(
                PostModel.is_deleted == False,
                PostModel.category_id == dto.post_category,
                PostModel.category_detail_id == dto.post_category_detail,
            )
        )

        try:
            query = (
                session.query(PostModel)
                    .join(PostModel.article)
                    .join(PostModel.post_attachments)
                    .filter(*search_filter)
                    .order_by(PostModel.id.desc())
                    .order_by(PostAttachmentModel.id.desc())
            )
            post_list = query.all()
            article_list: Union[List[ArticleEntity], List] = self._get_article_entity(post_list)

            post_entities = list()
            for post, article in zip(post_list, article_list):
                post_entities.append(post.to_entity(article=article))
            return post_entities
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
