# -*- coding: utf-8 -*-
import json
from tornado import web, ioloop
from tornado.web import RequestHandler, Application

from task.RedisHelper import RedisClient


API_PORT = 8000


class MainHandler(RequestHandler):
    def initialize(self, redis):
        self.redis = redis

    def get(self, api=''):
        if not api:
            links = ['random', 'batch', 'all', 'count']
            self.write('<h4>Welcome to Proxy API</h4>')
            for link in links:
                self.write('<a href=' + link + '>' + link + '</a><br>')
        if api == 'random':
            result = self.redis.random()
            if result:
                result = result.split(":")
                ip = result[0]
                port = result[1]
                self.write('<a>IP: {0}, Port: {1}'.format(ip, port))
        if api == 'batch':
            result = self.redis.batch(0, 20)
            if result:
                self.write(json.dumps(result))
        if api == 'all':
            result = self.redis.all()
            if result:
                self.write(json.dumps(result))
        if api == 'count':
            self.write(str(self.redis.count()))


def server(redis, port=API_PORT, address=''):
    application = Application([
        (r'/', MainHandler, dict(redis=redis)),
        (r'/(.*)', MainHandler, dict(redis=redis)),
    ])
    application.listen(port, address=address)
    print("API Listening on", port)
    ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    redis = RedisClient()
    server(redis)

