import inject
import boto3

from flask import current_app

from app.extensions.queue import SqsTypeEnum, SenderDto
from app.extensions.utils.log_helper import logger_
from core.domains.user.enum.user_enum import UserSqsTypeEnum

logger = logger_.getLogger(__name__)


class SqsMessageSender:
    @inject.autoparams()
    def __init__(self):
        self.__target_q = None

        self.__sqs = boto3.client(
            "sqs",
            region_name=current_app.config["AWS_REGION_NAME"],
            aws_access_key_id=current_app.config["AWS_ACCESS_KEY"],
            aws_secret_access_key=current_app.config["AWS_SECRET_ACCESS_KEY"],
        )

    def send_message(
            self,
            queue_type: SqsTypeEnum = None,
            msg: SenderDto = None,
            logging: bool = False,
    ) -> bool:
        try:
            if not self.__target_q:
                self.__target_q = (
                        current_app.config["SQS_BASE"]
                        + "/"
                        + current_app.config[queue_type.value]
                )
                logger.debug(
                    "[SqsMessageSender][Set] Target Queue {0}".format(self.__target_q)
                )

            response = self.__sqs.send_message(
                QueueUrl=self.__target_q,
                DelaySeconds=0,
                MessageAttributes={},
                MessageBody=msg.to_json(),
                MessageGroupId=UserSqsTypeEnum.SEND_USER_DATA_TO_LAKE.value
            )

            if logging:
                logger.info("🚀[SqsMessageSender][Send] {0}".format(response))
            return True

        except Exception as e:
            logger.error(
                "[SqsMessageSender][send_message][Exception] {0}".format(e)
            )
            return False

    def receive_after_delete(
            self,
            queue_type: SqsTypeEnum = None,
    ) -> bool:
        while True:
            if not self.__target_q:
                self.__target_q = (
                        current_app.config["SQS_BASE"]
                        + "/"
                        + current_app.config[queue_type.value]
                )
                logger.debug(
                    "[receive_after_delete] Target Queue {0}".format(self.__target_q)
                )

            # SQS에 큐가 비워질때까지 메세지 조회
            resp = self.__sqs.receive_message(
                QueueUrl=self.__target_q,
                AttributeNames=['All'],
                MaxNumberOfMessages=10
            )

            try:
                """
                제너레이터는 함수 끝까지 도달하면 StopIteration 예외가 발생. 
                마찬가지로 return도 함수를 끝내므로 return을 사용해서 함수 중간에 빠져나오면 StopIteration 예외가 발생.
                특히 제너레이터 안에서 return에 반환값을 지정하면 StopIteration 예외의 에러 메시지로 들어감
                """
                yield from resp['Messages']
            except KeyError:
                # not has next
                return False

            entries = [
                {'Id': msg['MessageId'], 'ReceiveHandle': msg['ReceiveHandle']}
                for msg in resp['Messages']
            ]

            resp = self.__sqs.delete_message_batch(
                QueueUrl=self.__target_q, Entries=entries
            )

            if len(resp['Successful']) != len(entries):
                raise RuntimeError(
                    f"Failed to delete messages: entries={entries!r} resp={resp!r}"
                )
