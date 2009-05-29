from webob.exc import *
from webob import Request

def redirect(url, req_old):
    exc = HTTPTemporaryRedirect(location=url)
    req = req_old.copy_get()
    resp = req.get_response(exc)
    resp.delete_cookie('login')
    for k, v in req.cookies.iteritems():
        resp.set_cookie(k, v)
    return resp 


