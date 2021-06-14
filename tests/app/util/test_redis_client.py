from random import randint

import pytest

from app.extensions.cache.cache import RedisClient
from app.extensions.utils.enum.cache_enum import RedisKeyPrefix, RedisExpire


@pytest.mark.skip(reason="local redis 실행 안할경우 편의상 skip")
def test_set_value_to_redis_when_send_mobile_auth_number_then_success(
    redis: RedisClient,
):
    phone_number = "01044744412"
    auth_number = str(randint(1000, 10000))
    if redis.is_available:
        key = f"{RedisKeyPrefix.MOBILE_AUTH.value}:{phone_number}"
        redis.set(
            key=key, value=auth_number, ex=RedisExpire.MOBILE_AUTH_TIME.value,
        )

        get_redis_value = redis.get_by_key(key)
        assert str(get_redis_value.decode("utf-8")) == auth_number

        # before delete key -> 1
        redis.is_exists(key)
        assert redis.is_exists(key) == 1

        # after delete key -> 0
        redis.delete(key)
        assert redis.is_exists(key) == 0
