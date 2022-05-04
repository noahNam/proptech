import json
import uuid

from app import redis
from app.extensions.utils.log_helper import logger_

logger = logger_.getLogger(__name__)

"""
    message pulling test용 worker
"""


class SetRedisUseCase:
    def __init__(self,):
        self._redis = redis
        # self._redis = redis.Redis(host='localhost', port=6379, db=0)

    def execute(self) -> None:
        """
        PRIVATE_SALES = "sync-I-private-sales-1={...}"
        key = sync(유형)-CRUD유형(I,U)-private-sales(테이블)-pk(1):value
        CRUD유형 
            1. I -> Insert with PK
            2. IA -> Insert with Auto-increment PK
            3. U -> Update with PK
        """

        is_available = self._redis.is_available()
        logger.info(f"----> is_available : {is_available}")

        key1 = "sync:U:private_sales:1"
        data = dict(id=1, name="광영1")
        message1 = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self._redis.set(key=key1, value=message1)

        key2 = "sync:U:private_sales:2"
        data = dict(id=2, name="양지2")
        message2 = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self._redis.set(key=key2, value=message2)

        key3 = "sync:U:private_sales:3"
        data = dict(id=3, name="벨라3")
        message3 = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self._redis.set(key=key3, value=message3)

        key4 = "sync:U:private_sales:4"
        data = dict(id=4, name="신원4")
        message4 = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self._redis.set(key=key4, value=message4)

        key5 = "sync:U:public_sales:2"
        data = dict(id=2, name="서희2")
        message5 = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self._redis.set(key=key5, value=message5)

        key6 = "sync:U:public_sales:9"
        data = dict(id=9, name="트루엘9")
        message6 = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self._redis.set(key=key6, value=message6)

        # Insert with PK
        key7 = "sync:I:general_supply_results:9"
        data = dict(
            id=900000,
            public_sale_details_id=106986,
            region="해당지역900",
            region_percent=900,
            win_point=900,
        )
        message7 = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self._redis.set(key=key7, value=message7)

        # Insert with Auto-increment PK
        token = str(uuid.uuid4())
        key8 = f"sync:IA:general_supply_results:{token}"
        data = dict(
            public_sale_details_id=106986,
            region="해당지역999",
            region_percent=999,
            win_point=999,
        )
        message8 = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self._redis.set(key=key8, value=message8)

        get_key = self._redis.get_by_key(key=key1)
        logger.info(f"*** get_key *** {get_key}")

        get_key = self._redis.get_by_key(key=key2)
        logger.info(f"*** get_key *** {get_key}")

        get_key = self._redis.get_by_key(key=key3)
        logger.info(f"*** get_key *** {get_key}")

        get_key = self._redis.get_by_key(key=key4)
        logger.info(f"*** get_key *** {get_key}")

        get_key = self._redis.get_by_key(key=key5)
        logger.info(f"*** get_key *** {get_key}")

        get_key = self._redis.get_by_key(key=key6)
        logger.info(f"*** get_key *** {get_key}")

        get_key = self._redis.get_by_key(key=key7)
        logger.info(f"*** get_key *** {get_key}")

        get_key = self._redis.get_by_key(key=key8)
        logger.info(f"*** get_key *** {get_key}")
