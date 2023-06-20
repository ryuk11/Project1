"""
Script to configure the file logger and the starting point of execution
"""
import logging
import os
import pathlib
from logging.handlers import RotatingFileHandler
from werkzeug.middleware.proxy_fix import ProxyFix

import cherrypy

from app import application
application.wsgi_app = ProxyFix(application.wsgi_app)
cherrypy.tree.graft(application.wsgi_app, '/')
cherrypy.config.update({'server.socket_host': '0.0.0.0',
                        'server.socket_port': 5000,
                        'engine.autoreload.on': False,
                        })

if __name__ == '__main__':
    try:
	
        formatter = logging.Formatter(
            "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
        handler = RotatingFileHandler(
            f'{os.path.join(pathlib.Path(__file__).parent.absolute(), "logs", "application.log")}',
            maxBytes=10000, backupCount=1)

        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        application.logger.addHandler(handler)
        application.logger.setLevel(logging.DEBUG)
        cherrypy.engine.start()
    except KeyboardInterrupt:
        cherrypy.engine.stop()
