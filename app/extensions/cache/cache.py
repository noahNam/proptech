from datetime import timedelta
from typing import Union, Optional, Any

import redis
from flask import Flask
from redis import RedisError

from app.extensions.utils.log_helper import logger_

logger = logger_.getLogger(__name__)


class RedisClient:
    CONFIG_NAME = "REDIS_URL"

    def __init__(self):
        self._redis_client: redis.Redis = redis.Redis
        self.keys = None
        self.copied_keys = []

    def init_app(self, app: Flask, url=None):
        redis_url = url if url else app.config.get(RedisClient.CONFIG_NAME)
        self._redis_client = self._redis_client.from_url(redis_url)

    def scan_pattern(self, pattern: str) -> None:
        self.keys = self._redis_client.scan_iter(pattern)

    def get_after_scan(self) -> Optional[dict]:
        try:
            key = next(self.keys)
            value = self._redis_client.get(key)
            self.copied_keys.append(key)
            return {"key": key, "value": value}
        except StopIteration as e:
            return None

    def set(self, key: Any, value: Any, ex: Union[int, timedelta] = None,) -> Any:
        return self._redis_client.set(name=key, value=value, ex=ex)

    def clear_cache(self) -> None:
        for key in self.copied_keys:
            self._redis_client.delete(key)
        self.keys = None
        self.copied_keys = []

    def get_by_key(self, key: any) -> str:
        return self._redis_client.get(name=key)

    def flushall(self) -> None:
        self._redis_client.flushall()

    def disconnect(self) -> None:
        self._redis_client.connection_pool.disconnect()

    def sadd(self, set_name: Any, values: Any) -> Any:
        return self._redis_client.sadd(set_name, values)

    def expire(self, key: Any, time: Union[int, timedelta]) -> Any:
        return self._redis_client.expire(name=key, time=time)

    def is_available(self):
        try:
            self._redis_client.ping()
        except RedisError:
            logger.error(f"[RedisClient][is_available] ping error")
            return False
        return True

    def sismember(self, set_name: Any, value: Any) -> bool:
        return self._redis_client.sismember(name=set_name, value=value)

    def smembers(self, set_name: Any) -> Any:
        return self._redis_client.smembers(name=set_name)

    def is_exists(self, set_name: Any) -> Any:
        return self._redis_client.exists(set_name)

    def delete(self, key: Any) -> Any:
        return self._redis_client.delete(key)
