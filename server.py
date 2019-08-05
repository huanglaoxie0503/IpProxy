# -*- coding: utf-8 -*-
from task.api import server
from task.RedisHelper import RedisClient

redis = RedisClient()
server(redis)



