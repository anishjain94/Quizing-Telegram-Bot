from config.environment import *

import redis

redisClient = redis.Redis(
    host=redisHost,
    port=redisPort,
    password=redisPassword,
    decode_responses=True)
