import io
import os
from datetime import datetime
from pathlib import Path
from typing import List
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
    def upload(cls, bucket, dir_name, file_name, object_name, extension):
        """
        :param bucket: s3 bucket
        :param file_name: 파일
        :param dir_name: 폴더 이름
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
            f = open(file_name, "rb")
            loaded_image = Image.open(f)
            buffer = io.BytesIO()
            loaded_image.save(buffer, extension)
            buffer.seek(0)
            client.put_object(
                Body=buffer, Bucket=bucket, Key=object_name, ContentType="image/*"
            )
            f.close()
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
    def get_image_upload_uuid_path(cls, image_table_name, dir_name, extension):
        image_table_name = image_table_name
        dir_name = dir_name
        ymd_path = str(datetime.now().year)
        uuid_name = str(uuid4())
        extension = extension

        return "/".join(
            [image_table_name, dir_name, ymd_path, uuid_name + "." + extension,]
        )


class ImageHelper:
    @classmethod
    def get_image_upload_dir(cls):
        app_dir = Path(__file__).resolve(strict=True).parent
        return os.path.join(app_dir, "upload_images_list")


class ImageNameCollector:
    def __init__(self, target_dir: str):
        self._target_dir = target_dir
        self._collect_dict_list = list()

    @property
    def collect_dict_list(self):
        return self._collect_dict_list

    def get_file_list(self):
        for (roots, dirs, file_names) in os.walk(self._target_dir):
            # roots 기준 1 depth 하위 dir
            dir_ = roots.split(r"/")[-1]
            if self._has_valid_bracket(dir_or_file_name=dir_):
                if len(file_names) > 0:
                    self._collect_dict_list.append({dir_: file_names})

    def _has_valid_bracket(self, dir_or_file_name: str):
        if not dir_or_file_name:
            return False

        front_bracket = 0
        back_bracket = 0

        for idx in range(len(dir_or_file_name)):
            if dir_or_file_name[idx] == "(":
                front_bracket = front_bracket + 1
            elif dir_or_file_name[idx] == ")":
                back_bracket = back_bracket + 1

        if front_bracket != 1 or back_bracket != 1:
            return False
        return True

    def _get_pk_inside_bracket(self, string_with_bracket: str):
        try:
            return int(string_with_bracket.split("(")[1].rsplit(")")[0])
        except Exception as e:
            logger.error(f"[ImageNameCollector][_get_pk_inside_bracket]: Error - {e}")
            return string_with_bracket

    def get_public_sale_photos_ids(self, dir_name_list: List[str]):
        ids = list()
        passed_dirs = list()

        for dir_name in dir_name_list:
            id_ = self._get_pk_inside_bracket(string_with_bracket=dir_name)
            if type(id_) is int:
                ids.append(self._get_pk_inside_bracket(string_with_bracket=dir_name))
            else:
                passed_dirs.append(dir_name)

        return ids, passed_dirs
