import config
import mimetypes
from webob import Response, Request

def static(req, file):
    type, encoding = mimetypes.guess_type(file)
    if not type:
        type = 'application/octet-stream'

    print "static files:" + config.staticfiles
    pathfile = config.staticfiles + "/" + file
    res = Response(content_type=type)
    res.body = open(pathfile, 'rb').read()
    return res
