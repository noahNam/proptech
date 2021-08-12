import os
from enum import Enum


class AwsServiceEnum(Enum):
    S3 = "s3"


class S3BucketEnum(Enum):
    TOADHOME_BUCKET_NAME = os.environ.get("TOADHOME_BUCKET_NAME")


class S3PathEnum(Enum):
    PROFILE_IMGS = "profile_imgs/"


class S3RegionEnum(Enum):
    TOADHOME_BUCKET_REGION = os.environ.get("TOADHOME_BUCKET_REGION")


class CloudFrontEnum(Enum):
    TOADHOME_CLOUD_FRONT_DOMAIN = os.environ.get("TOADHOME_CLOUD_FRONT_DOMAIN")
