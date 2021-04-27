import boto3
from botocore.exceptions import ClientError
from flask import current_app
from app.extensions.utils.enum.aws_enum import AwsServiceEnum
from app.extensions.utils.log_helper import logger_

logger = logger_.getLogger(__name__)


class S3Helper:
    @classmethod
    def upload(cls, bucket, file_name, object_name):
        """
        :param bucket: s3 bucket
        :param file_name: 파일
        :param object_name: 저장할 경로 + 파일
        :return:
        """
        client = boto3.client(
            AwsServiceEnum.S3.value,
            aws_access_key_id=current_app.config.get("AWS_ACCESS_KEY"),
            aws_secret_access_key=current_app.config.get("AWS_SECRET_ACCESS_KEY"),
        )

        try:
            client.put_object(Body=file_name, Bucket=bucket, Key=object_name)
        except ClientError as e:
            logger.error(
                f"[S3Helper][upload] bucket : {bucket} file_name : {file_name} error : {e}"
            )
            return False
        except Exception as e:
            logger.error(
                f"[S3Helper][upload] bucket : {bucket} file_name : {file_name} error : {e}"
            )
            return False
        return True
