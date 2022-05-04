import json
import os
from time import sleep
from typing import Dict, List, Union

import inject

from app import redis
from app.extensions.utils.log_helper import logger_
from app.persistence.model import PublicSaleModel, PrivateSaleModel, GeneralSupplyResultModel
from core.domains.house.repository.house_repository import HouseRepository

logger = logger_.getLogger(__name__)

model_transfer_dict = dict(public_sales=PublicSaleModel, private_sales=PrivateSaleModel, general_supply_results=GeneralSupplyResultModel)


class SyncDataUseCase:
    @inject.autoparams()
    def __init__(
            self,
            topic: str,
            house_repo: HouseRepository,
    ):
        self.topic = topic
        self._redis_client = redis
        self._house_repo = house_repo
        self._is_insert_failure = False
        self._is_update_failure = False

    @property
    def client_id(self) -> str:
        return f"{self.topic}-{os.getpid()}"

    def execute(self) -> None:
        """
        PRIVATE_SALES = "sync-I-private-sales-1={...}"
        key = sync(유형)-CRUD유형(I,U)-private-sales(테이블)-pk(1):value
        CRUD유형
            1. I -> Insert with PK
            2. IA -> Insert with Auto-increment PK
            3. U -> Update with PK
        """

        logger.info(f"🚀\tSyncDataUseCase Start - {self.client_id}")
        while True:
            messages = None

            try:
                # Insert Model
                self._redis_client.scan(pattern="sync:I*")
                messages = self._get_messages()

                if messages:
                    logger.info(f"[*] Get length of insert sync data -> {self._get_sync_data_len(messages=messages)}")

                    self._insert_target_model(messages=messages)
                    logger.info("🚀\tInsert target model success")
            except Exception as e:
                logger.exception(f"☠️\tError insert process. {e}")
                self._is_insert_failure = True

            if self._is_insert_failure:
                failure_list: Union[List[Dict], List] = self._transfer_sync_failure_history_entity(messages=messages)
                self._house_repo.bulk_insert_sync_failure_histories(insert_list=failure_list)
                self._is_insert_failure = False

            try:
                # Update Model
                self._redis_client.scan(pattern="sync:U*")
                messages = self._get_messages()

                if messages:
                    logger.info(f"[*] Get length of update sync data -> {self._get_sync_data_len(messages=messages)}")

                    self._update_target_model(messages=messages)
                    logger.info("🚀\tUpdate target model success")
            except Exception as e:
                logger.exception(f"☠️\tError update process. {e}")
                self._is_update_failure = True

            if self._is_update_failure:
                failure_list: Union[List[Dict], List] = self._transfer_sync_failure_history_entity(messages=messages)
                self._house_repo.bulk_insert_sync_failure_histories(insert_list=failure_list)
                self._is_update_failure = False

            # Clear cache
            if self._redis_client.copied_keys:
                logger.info(f"🚀️\t Clear key length -> {len(self._redis_client.copied_keys)}")
                logger.info(f"🚀️\t Clear keys -> {self._redis_client.copied_keys}")
                self._redis_client.clear_cache()


    def _transfer_sync_failure_history_entity(self, messages: Dict) -> Union[List[Dict], List]:
        failure_list = list()
        for key in messages.keys():
            message = messages.get(key)

            for sync_data in message:
                sync_failure_histories_dict = dict(
                    target_table=key,
                    sync_data=sync_data,
                )

                failure_list.append(sync_failure_histories_dict)
        return failure_list

    def _get_sync_data_len(self, messages: Dict) -> int:
        cnt = 0
        if messages:
            for message in messages:
                cnt += len(messages.get(message))
        return cnt

    def _get_messages(self) -> Dict:
        # limit 만큼 메세지를 scan (10000이면 메세지 10000개를 스캔)
        offset = 0
        limit = 10000

        messages = dict()
        while True:
            try:
                data = self._redis_client.get_after_scan()
                if data is None or offset >= limit:
                    break

                key = data["key"].decode().split(":")[2]
                messages.setdefault(key, []).append(json.loads(data["value"]))
                offset += 1
            except Exception as e:
                logger.info("_get_messages() exception")
                logger.exception(str(e))
                break

        return messages

    def _insert_target_model(self, messages: Dict) -> None:
        for key in model_transfer_dict.keys():
            # limit 만큼 메세지를 끊어서 처리
            offset = 0
            limit = 10000

            message = messages.get(key)
            if not message:
                continue

            model = model_transfer_dict.get(key)

            if len(message) > limit:
                while True:
                    insert_data = message[offset:offset+limit]
                    if not insert_data:
                        break
                    self._house_repo.bulk_insert_target_model(model=model, insert_list=insert_data)
                    offset += limit
            else:
                self._house_repo.bulk_insert_target_model(model=model , insert_list=message)

    def _update_target_model(self, messages: Dict) -> None:
        for key in model_transfer_dict.keys():
            # limit 만큼 메세지를 끊어서 처리
            offset = 0
            limit = 10000

            message = messages.get(key)
            if not message:
                continue

            model = model_transfer_dict.get(key)

            if len(message) > limit:
                while True:
                    update_data = message[offset:offset+limit]
                    if not update_data:
                        break
                    self._house_repo.bulk_update_target_model(model=model, update_list=update_data)
                    offset += limit
            else:
                self._house_repo.bulk_update_target_model(model=model, update_list=message)