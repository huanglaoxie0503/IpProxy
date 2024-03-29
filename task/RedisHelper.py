# -*- coding: utf-8 -*-
import redis
import re
from random import choice

from task.settings import REDIS_HOST, REDIS_PASSWORD, REDIS_DB, REDIS_PORT, REDIS_KEY, MAX_SCORE, MIN_SCORE, INITIAL_SCORE


class RedisClient(object):
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=REDIS_DB):
        """
        初始化
        :param host: Redis 地址
        :param port: Redis 端口
        :param password: Redis密码
        """
        self.db = redis.StrictRedis(host=host, port=port, password=password, db=db, decode_responses=True)

    def add(self, proxy, score=INITIAL_SCORE):
        """
        添加代理，设置分数为最高
        :param proxy: 代理
        :param score: 分数
        :return: 添加结果
        """
        if not re.match('\d+\.\d+\.\d+\.\d+\:\d+', proxy):
            print('代理不符合规范', proxy, '丢弃')
            return
        if not self.db.zscore(REDIS_KEY, proxy):
            return self.db.zadd(REDIS_KEY, score, proxy)

    def random(self):
        """
        随机获取有效代理，首先尝试获取最高分数代理，如果不存在，按照排名获取，否则异常
        :return: 随机代理
        """
        result = self.db.zrangebyscore(REDIS_KEY, MAX_SCORE, MAX_SCORE)
        if len(result):
            return choice(result)
        else:
            result = self.db.zrevrange(REDIS_KEY, 0, 100)
            if len(result):
                return choice(result)

    def decrease(self, proxy):
        """
        代理值减一分，小于最小值则删除
        :param proxy: 代理
        :return: 修改后的代理分数
        """
        score = self.db.zscore(REDIS_KEY, proxy)
        if score and score > MIN_SCORE:
            print('代理', proxy, '当前分数', score, '减1')
            return self.db.zincrby(REDIS_KEY, proxy, -1)
        else:
            print('代理', proxy, '当前分数', score, '移除')
            return self.db.zrem(REDIS_KEY, proxy)

    def exists(self, proxy):
        """
        判断是否存在
        :param proxy: 代理
        :return: 是否存在
        """
        return not self.db.zscore(REDIS_KEY, proxy) == None

    def max(self, proxy):
        """
        将代理设置为MAX_SCORE
        :param proxy: 代理
        :return: 设置结果
        """
        print('代理', proxy, '可用，设置为', MAX_SCORE)
        return self.db.zadd(REDIS_KEY, MAX_SCORE, proxy)

    def count(self):
        """
        获取数量
        :return: 数量
        """
        return self.db.zcard(REDIS_KEY)

    def all(self):
        """
        获取全部代理
        :return: 全部代理列表
        """
        return self.db.zrangebyscore(REDIS_KEY, MIN_SCORE, MAX_SCORE)

    def batch(self, start, stop):
        """
        批量获取
        :param start: 开始索引
        :param stop: 结束索引
        :return: 代理列表
        """
        return self.db.zrevrange(REDIS_KEY, start, stop - 1)


if __name__ == '__main__':
    conn = RedisClient()
    result = conn.all()
    print(result)


#
# class RedisClient(object):
#     def __init__(self):
#         self.host = REDIS_HOST
#         self.password = REDIS_PASSWORD
#         self.db = REDIS_DB
#         self.port = REDIS_PORT
#         self.key = REDIS_KEY
#
#         self.redis_client = redis.StrictRedis(host=self.host, port=self.port, password=self.password, db=self.db, decode_responses=True)
#
#     def set(self, name, proxy):
#         # 设置代理
#         return self.redis_client.hset(self.key, name, proxy)
#
#     def get(self, name):
#         # 获取代理
#         return self.redis_client.hget(self.key, name)
#
#     def count(self):
#         # 获取代理总数
#         return self.redis_client.hlen(self.key)
#
#     def remove(self, name):
#         # 删除代理
#         return self.redis_client.hdel(self.key, name)
#
#     def names(self):
#         # 获取主机名称列表
#         return self.redis_client.hkeys(self.key)
#
#     def proxies(self):
#         # 获取代理列表
#         return self.redis_client.hvals(self.key)
#
#     def random(self):
#         # 随机获取代理
#         proxies = self.proxies()
#         return random.choice(proxies)
#
#     def all(self):
#         # 获取字典
#         return self.redis_client.hgetall(self.key)
#
#
# if __name__ == '__main__':
#     conn = RedisClient()
#     result = conn.random()
#     print(result)