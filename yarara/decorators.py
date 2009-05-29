#! -* coding: utf8 *-
from webob import Request, Response
from webob import exc


def controller(func):
    """
    esto no deberia ser un controller... 
    no me gusta asi... 
    es poco extensible, tendria un monton de codigo
    para ver diferentes response a partir de los request
    como es el caso de las imagenes y files.
    ---
    mejor hacer una funcion como http_response(string) y
    luego mime_response(string) o static_response(string), 
    y el servidor solo debería ejecutar el response.

    render internamente deberia usar http_response() algo asi:
    def render(tpl, vars):
        htmlstr = codigo de render de hoy
        return http_response(htmlstr)
    """
    def replacement(environ, start_response):
        req = Request(environ)
        try:
            resp = func(req, **req.urlvars)
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
                #-----------------------------
                #print ">"*25
                #print d
                #print ">"*25
                #-----------------------------
                for k, v in req.cookies.iteritems():
                    if not d.has_key(k):
                        resp.set_cookie(k, v)
                for k, v in d.iteritems():
                    if not req.cookies.has_key(k):
                        resp.delete_cookie(k)
                #-----------------------------
                #print "#"*20 + "cookies"
                #print req.cookies
                #print "#"*20 + " response"
                #print resp.headers.keys()
                #print "#"*20 + " request"
                #print req.headers['Cookie']
                #-----------------------------
            else:
                for k, v in req.cookies.iteritems():
                    resp.set_cookie(k, v)
        elif isinstance(resp, Response):
            return resp(environ, start_response)
        return resp(environ, start_response)
    return replacement


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
