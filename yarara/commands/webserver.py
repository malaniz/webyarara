#!/usr/bin/env python
from routes import router
from elixir import *
import config
from models import *
from processing import Process


def syncronize_db():
    metadata.bind = config.metadata
    metadata.bind.echo = False
    setup_all(True)

def launch_server():
    try:
        print "Running server ... "
        syncronize_db()
        httpserver.serve(router, config.host, config.port)
    except KeyboardInterrupt:
        print "^C shutting down server"

   
class Server(object):
    def run(self):
        p = Process(target=launch_server)
        p.start()
        p.join()
        while True:
            if change_code():
                p.terminate()
                p = Process(target=launch_server)
                p.start()
 

