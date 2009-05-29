from webob import Request, Response
from webob import exc

def http_response(controller):
    def deco(environ, start_response):
        req = Request(environ)
        try:
            resp = controller(req, **req.urlvars)
        except exc.HTTPException, e:
            resp = e.trace()

def static_response(controller):
    def deco(environ, start_response):
        try:
            resp = controller(req, **req.urlvars)
        except exc.HTTPException, e:
            resp = e.trace()
        #if isinstance(resp, Response):
        return resp(environ, start_response)
    return deco    


def http_response(controller):
    def deco(environ, start_response):
        req = Request(environ)
        try:
            resp = controller(req, **req.urlvars)
        except exc.HTTPException, e:
            resp = e.trace()
        if isinstance(resp, basestring):
            resp = Response(body=resp)
            if req.headers.has_key('Cookie'):
                l = req.headers['Cookie'].split(';')
                d = dict()
                for x in l:
                    k, v = x.split('=',1)
                    k = k.strip()
                    v = v.strip()
                    d[k] = v
                for k, v in req.cookies.iteritems():
                    if not d.has_key(k):
                        resp.set_cookie(k, v)
                for k, v in d.iteritems():
                    if not req.cookies.has_key(k):
                        resp.delete_cookie(k)
            else:
                for k, v in req.cookies.iteritems():
                    resp.set_cookie(k, v)
        return resp(environ, start_response)
    return deco


def build_cookies(req, resp):
    if req.headers.has_key('Cookie'):
        l = req.headers['Cookie'].split(';')
        d = dict()
        for x in l:
            k, v = x.split('=', 1)
            k = k.strip()
            v = v.strip()
            d[k] = v
        for k, v in req.cookies.iteritems():
            if not d.has_key(k):
                resp.set_cookie(k, v)
        for k, v in d.iteritems():
            if not req.cookies.has_key(k):
                resp.delete_cookie(k)
    else:
        for k, v in req.cookies.iteritems():
            resp.set_cookie(k, v)
