from enum import Enum


class AwsServiceEnum(Enum):
    S3 = "s3"


class S3BucketEnum(Enum):
    APARTALK_BUCKET = "test-apartalk-bucket"


class S3PathEnum(Enum):
    PROFILE_IMGS = "profile_imgs/"
