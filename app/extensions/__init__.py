from flask_jwt_extended import JWTManager

from app.extensions.cache.cache import RedisClient
from app.extensions.sens.sms import SmsClient

jwt = JWTManager()
sms = SmsClient()
redis = RedisClient()
