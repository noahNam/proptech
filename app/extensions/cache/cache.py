import abc
from datetime import timedelta
from typing import Union, Optional, Any

import redis
from flask import Flask
from redis import RedisError
from rediscluster import RedisCluster

from app.extensions.utils.log_helper import logger_

logger = logger_.getLogger(__name__)


class Cache:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def scan(self, pattern: str) -> None:
        pass

    @abc.abstractmethod
    def get_after_scan(self) -> Optional[dict]:
        pass

    @abc.abstractmethod
    def set(self, key: Any, value: Any, ex: Union[int, timedelta] = None,) -> None:
        pass

    @abc.abstractmethod
    def clear_cache(self) -> None:
        pass

    @abc.abstractmethod
    def get_by_key(self, key: str) -> str:
        pass

    @abc.abstractmethod
    def flushall(self) -> None:
        pass

    @abc.abstractmethod
    def is_available(self) -> None:
        pass


class RedisClient(Cache):
    CONFIG_NAME = "REDIS_URL"
    CLUSTER_NODE_1 = "REDIS_NODE_HOST_1"
    CLUSTER_NODE_2 = "REDIS_NODE_HOST_2"

    def __init__(self):
        self._redis_client = redis.Redis
        self.keys = None
        self.copied_keys = []

    def get_cluster_nodes(self, app: Flask):
        cluster_nodes = [RedisClient.CLUSTER_NODE_1, RedisClient.CLUSTER_NODE_2]
        startup_node_list = list()
        for node_host in cluster_nodes:
            node = dict()
            node["host"] = app.config.get(node_host)
            node["port"] = 6379
            startup_node_list.append(node)
        return startup_node_list

    def init_app(self, app: Flask, url=None):
        if app.config.get("REDIS_NODE_HOST_1"):
            startup_nodes = self.get_cluster_nodes(app=app)
            self._redis_client: RedisCluster = RedisCluster(
                startup_nodes=startup_nodes,
                decode_responses=False,
                skip_full_coverage_check=True,
            )
        else:
            redis_url = url if url else app.config.get(RedisClient.CONFIG_NAME)
            self._redis_client = self._redis_client.from_url(redis_url)
            test = 1

    def scan(self, pattern: str) -> None:
        self.keys = self._redis_client.scan_iter(match=pattern)

    def get_after_scan(self) -> Optional[dict]:
        try:
            key = next(self.keys)
            value = self._redis_client.get(key).decode("utf-8")
            self.copied_keys.append(key)
            return {"key": key, "value": value}
        except StopIteration:
            return None

    def set(self, key: Any, value: Any, ex: Union[int, timedelta] = None,) -> None:
        self._redis_client.set(name=key, value=value, ex=ex)

    def clear_cache(self) -> None:
        for key in self.copied_keys:
            self._redis_client.delete(key)
        self.keys = None
        self.copied_keys = []

    def get_by_key(self, key: str) -> str:
        return self._redis_client.get(name=key).decode("utf-8")

    def flushall(self) -> None:
        self._redis_client.flushall()

    def is_available(self):
        try:
            self._redis_client.ping()
        except RedisError:
            logger.error(f"[RedisClient][is_available] ping error")
            return False
        return True
