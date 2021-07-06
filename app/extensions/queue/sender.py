from app.extensions.queue import SqsTypeEnum, SenderDto


class QueueMessageSender:
    def send_message(
        self, queue_type: SqsTypeEnum, msg: SenderDto = None, logging: bool = False,
    ) -> bool:
        pass
