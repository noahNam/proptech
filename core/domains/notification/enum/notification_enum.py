from enum import Enum


class NotificationStatusEnum(Enum):
    """
        notifications.status value
    """

    WAIT = 0
    SUCCESS = 1
    FAILURE = 2


class NotificationBadgeTypeEnum(Enum):
    """
        notifications.badge_type value
    """

    ALL = "all"
    IN = "in"
    OUT = "out"


class DeviceTypeEnum(Enum):
    PUSH = "push"
    SMS = "sms"
    EMAIL = "email"


class NotificationPushTypeEnum(Enum):
    """
        Push 대분류
        OFFICIAL = 공지 Push
        PRIVATE = 개인화 Push
        MARKETING = 마케 Push

        사용처 : 1. 코드레벨에서 사용처 현재 없음. 설정쪽에서 같은 value를 쓰기는 하지만 Enum을 가져와서 사용하지는 않음 (Parameter로 동일 value 값이 바로 들어옴)
                    1-1. UpdateReceiveNotificationSettingUseCase 에서 유저 마케팅 동의여부 체크 용도로 사용. 그외 사용처 없음.
               2. 추후 Push 고도화 시 코드레벨에서도 필요할 듯 하여 남겨둠.
               3. AWS SNS Topic Level로 사용중
    """

    OFFICIAL = "official"
    PRIVATE = "private"
    MARKETING = "marketing"


class NotificationTopicEnum(Enum):
    """
        Push 중분류
        OFFICIAL = 공지
        SUB_NEWS = 모집공고일, 당첨자발표일
        SUB_SCHEDULE = 특별공급일, 1순위, 2순위 날짜
        MARKETING = 마케팅

        사용처 : Push에 직접적으로 실리는 Topic
    """

    OFFICIAL = "apt001"
    SUB_NEWS = "apt002"
    SUB_SCHEDULE = "apt003"
    MARKETING = "apt004"


class NotificationHistoryCategoryEnum(Enum):
    """
        알림 조회 내역 조회 시 사용
        OFFICIAL = NotificationTopicEnum.OFFICIAL
        MY = NotificationTopicEnum.SUB_NEWS, NotificationTopicEnum.SUB_SCHEDULE
    """

    OFFICIAL = "official"
    MY = "my"
