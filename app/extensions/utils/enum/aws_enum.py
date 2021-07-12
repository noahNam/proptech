from enum import Enum


class AwsServiceEnum(Enum):
    S3 = "s3"


class S3BucketEnum(Enum):
    TOADHOME_BUCKET = "test-apartalk-bucket"


class S3PathEnum(Enum):
    PROFILE_IMGS = "profile_imgs/"


class S3RegionEnum(Enum):
    TOADHOME_REGION = "ap-northeast-2"
