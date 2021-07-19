from enum import Enum


class PostLimitEnum(Enum):
    LIMIT = 10


class PostCategoryEnum(Enum):
    NOTICE = 1
    FAQ = 2


class PostTypeEnum(Enum):
    ARTICLE = "article"
    ATTACHMENT = "attachment"
