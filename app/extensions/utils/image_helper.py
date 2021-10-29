import io
import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import boto3
from PIL import Image
from botocore.exceptions import ClientError
from flask import current_app

from app.extensions.utils.enum.aws_enum import (
    AwsServiceEnum,
    CloudFrontEnum,
)
from app.extensions.utils.log_helper import logger_

logger = logger_.getLogger(__name__)


class S3Helper:
    @classmethod
    def upload(cls, bucket, file_name, object_name, extension):
        """
        :param bucket: s3 bucket
        :param file_name: 파일
        :param object_name: 저장할 경로 + 파일
        :param object_name: 확장자
        :return:
        """
        result_flag = False
        client = boto3.client(
            service_name=AwsServiceEnum.S3.value,
            region_name=current_app.config.get("AWS_REGION_NAME"),
            aws_access_key_id=current_app.config.get("AWS_ACCESS_KEY"),
            aws_secret_access_key=current_app.config.get("AWS_SECRET_ACCESS_KEY"),
        )

        try:
            loaded_image = Image.open(file_name)
            buffer = io.BytesIO()
            loaded_image.save(buffer, extension)
            buffer.seek(0)
            if extension == 'jpg':
                content_type = "image/jpeg"
            else:
                content_type = f"image/{extension}"
            client.put_object(Body=buffer, Bucket=bucket, Key=object_name, ContentType="image/*")
        except ClientError as e:
            logger.error(
                f"[S3Helper][upload] bucket : {bucket} file_name : {file_name} error : {e}"
            )
        except Exception as e:
            logger.error(
                f"[S3Helper][upload] bucket : {bucket} file_name : {file_name} error : {e}"
            )
        else:
            result_flag = True

        return result_flag

    @classmethod
    def get_cloudfront_url(cls):
        return f"https://{CloudFrontEnum.TOADHOME_CLOUD_FRONT_DOMAIN.value}"

    @classmethod
    def get_image_upload_dir(cls):
        app_dir = Path(__file__).resolve(strict=True).parent
        return os.path.join(app_dir, "upload_images_list")

    @classmethod
    def get_image_upload_uuid_path(cls, image_table_name, extension):
        dir_name = image_table_name
        ymd_path = str(datetime.now().year)
        uuid_name = str(uuid4())
        extension = extension

        return "/".join([dir_name, ymd_path, uuid_name + "." + extension,])
