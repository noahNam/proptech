import os
from enum import Enum


class AwsServiceEnum(Enum):
    S3 = "s3"


class S3BucketEnum(Enum):
    TOADHOME_BUCKET = "test-apartalk-bucket"
    TANOS_S3_BUCKET = os.environ.get("TANOS_S3_BUCKET") or "test-apartalk-bucket"


class S3PathEnum(Enum):
    PROFILE_IMGS = "profile_imgs/"


class S3RegionEnum(Enum):
    TANOS_S3_REGION = os.environ.get("TANOS_S3_REGION") or "ap-northeast-2"
