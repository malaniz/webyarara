from routes import router 
from elixir import *
from jinja2 import Environment, FileSystemLoader
import config
from models import *

def dbrun():
    metadata.bind = config.metadata
    metadata.bind.echo = False 
    setup_all(True)


def run():
    dbrun()
    from paste import httpserver

    try:
        print "Running server ..."
        httpserver.serve(router, 
            config.host, 
            config.port
        )
    except KeyboardInterrupt:
        print "^C shutting down server"
   


if __name__ == '__main__':
    run()    

