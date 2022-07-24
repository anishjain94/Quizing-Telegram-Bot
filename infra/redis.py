import redis
from config.environment import *


redisClient = redis.Redis(
    host=redisHost,
    port=redisPort,
    password=redisPassword)
