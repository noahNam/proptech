import json
import os
from typing import Dict, List, Union

import inject

from app import redis
from app.extensions.utils.log_helper import logger_
from app.persistence.model import (
    PublicSaleModel,
    PrivateSaleModel,
    GeneralSupplyResultModel,
    RealEstateModel,
)
from core.domains.house.repository.house_repository import HouseRepository

logger = logger_.getLogger(__name__)

model_transfer_dict = dict(
    real_estates=RealEstateModel,
    public_sales=PublicSaleModel,
    private_sales=PrivateSaleModel,
    general_supply_results=GeneralSupplyResultModel,
)


class SyncDataUseCase:
    @inject.autoparams()
    def __init__(
        self, topic: str, house_repo: HouseRepository,
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
        version 1.
        PRIVATE_SALES = "sync:I:private-sales:1={...}"
        key = sync(유형):CRUD유형(I,U):private-sales(테이블):pk(1)=value
        CRUD유형
            1. I -> Insert with PK
            2. U -> Update with PK

        version 2.
        PRIVATE_SALES = "sync:private-sales:1={...}"
        key = sync(유형):private-sales(테이블):pk(1)=value
        """

        logger.info(f"🚀\tSyncDataUseCase Start - {self.client_id}")
        while True:
            messages = {}

            try:
                # Insert Model
                self._redis_client.scan(pattern="sync:*")
                messages: dict = self._get_messages()

                if messages:
                    logger.info(
                        f"[*] Get length of insert sync data -> {self._get_sync_data_len(messages=messages)}"
                    )

                    self._upsert_target_model(messages=messages)
                    logger.info("🚀\tInsert target model success")
            except Exception as e:
                logger.exception(f"☠️\tError insert process. {e}")
                self._is_insert_failure = True

            if self._is_insert_failure:
                failure_list: Union[
                    List[Dict], List
                ] = self._transfer_sync_failure_history_entity(messages=messages)
                self._house_repo.bulk_insert_sync_failure_histories(
                    insert_list=failure_list
                )
                self._is_insert_failure = False

            # Clear cache
            if self._redis_client.copied_keys:
                logger.info(
                    f"🚀️\t Clear key length -> {len(self._redis_client.copied_keys)}"
                )
                logger.info(f"🚀️\t Clear keys -> {self._redis_client.copied_keys}")
                self._redis_client.clear_cache()

    def _transfer_sync_failure_history_entity(
        self, messages: Dict
    ) -> Union[List[Dict], List]:
        failure_list = list()
        for key in messages.keys():
            message = messages.get(key)

            for sync_data in message:
                sync_failure_histories_dict = dict(
                    target_table=key, sync_data=sync_data,
                )

                failure_list.append(sync_failure_histories_dict)
        return failure_list

    def _get_sync_data_len(self, messages: Dict) -> int:
        cnt = 0
        if messages:
            for message in messages:
                cnt += len(messages.get(message))
        return cnt

    def _get_messages(self) -> dict:
        # limit 만큼 메세지를 scan (10000이면 메세지 10000개를 스캔)
        offset = 0
        limit = 10000

        messages = dict()
        while True:
            try:
                data = self._redis_client.get_after_scan()
                if data is None or offset >= limit:
                    break

                key = (
                    data["key"].decode().split(":")[1]
                )  # private_sales, public_sales ...
                messages.setdefault(key, []).append(json.loads(data["value"]))
                offset += 1
            except Exception as e:
                logger.info("_get_messages() exception")
                logger.exception(str(e))
                raise

        return messages

    def _upsert_target_model(self, messages: Dict) -> None:
        for key in model_transfer_dict.keys():
            # limit 만큼 메세지를 끊어서 처리
            insert_offset = 0
            update_offset = 0
            limit = 10000

            insert_data = list()
            update_data = list()

            message = messages.get(key)
            if not message:
                continue

            model = model_transfer_dict.get(key)

            if model == RealEstateModel:
                self.__set_coordinates(message=message)

            for data in message:
                is_exists = self._house_repo._is_exists_by_id(model=model, data=data)
                if not is_exists:
                    insert_data.append(data)
                else:
                    update_data.append(data)

            # insert
            if len(insert_data) > limit:
                while True:
                    data = insert_data[insert_offset : insert_offset + limit]
                    if not data:
                        break
                    self._house_repo.bulk_insert_target_model(
                        model=model, insert_list=data
                    )
                    insert_offset += limit

            elif insert_data and len(insert_data) <= limit:
                self._house_repo.bulk_insert_target_model(
                    model=model, insert_list=insert_data
                )

            # update
            if len(update_data) > limit:
                while True:
                    data = update_data[update_offset : update_offset + limit]
                    if not data:
                        break
                    self._house_repo.bulk_update_target_model(
                        model=model, update_list=data
                    )
                    update_offset += limit

            elif update_data and len(update_data) <= limit:
                self._house_repo.bulk_update_target_model(
                    model=model, update_list=update_data
                )

    def __set_coordinates(self, message: List[dict]):
        for insert_data in message:
            insert_data.update(
                {
                    "coordinates": f"SRID=4326;POINT({insert_data.get('x_vl')} {insert_data.get('y_vl')})"
                }
            )
