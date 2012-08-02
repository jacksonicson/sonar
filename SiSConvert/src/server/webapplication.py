# coding=CP1252

import logging as logger
import tornado
import urlconfig as urls
import configuration

# Setup the logical URL tree
handler_list = urls.generateUrlHandlerList()
logger.debug(handler_list)

settings = {
    "static_path": configuration.get_static_file_path(),
    "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    "login_url": "/login",
    "autoescape" : None,
}

application = tornado.web.Application(handler_list, **settings)
