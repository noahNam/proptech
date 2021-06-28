import inject
import boto3

from flask import current_app

from app.extensions.queue import SqsTypeEnum, SenderDto
from app.extensions.utils.log_helper import logger_

logger = logger_.getLogger(__name__)


class SqsMessageSender:
    @inject.autoparams()
    def __init__(self):
        self.__target_q = None

        self.__sender = boto3.client(
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

            response = self.__sender.send_message(
                QueueUrl=self.__target_q,
                DelaySeconds=0,
                MessageAttributes={},
                MessageBody=msg.to_json(),
            )

            if logging:
                logger.info("🚀[SqsMessageSender][Send] {0}".format(response))
            return True

        except Exception as e:
            logger.error(
                "[SqsMessageSender][send_message][Exception] {0}".format(e)
            )
            return False
