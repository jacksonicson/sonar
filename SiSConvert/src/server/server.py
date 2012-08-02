from tornadorpc import async, start_server
from tornadorpc.json import JSONRPCHandler
import logging as logger

######################################
# Bootstrapping code is here
######################################

if __name__ == '__main__':
    logger.info('starting web interface...')
    webapplication.application.listen(8886)
    
    tornado.ioloop.IOLoop.instance().start()
