from webob import Request, Response
from webob import exc
from decorators import controller
import re

var_regex = re.compile(r'''
    \{
    (\w+)
    (?::([^}]+))?
    \}
    ''', 
    re.VERBOSE
)


def template_to_regex(template):
    regex = ''
    last_pos = 0
    for match in var_regex.finditer(template):
        regex += re.escape(template[last_pos:match.start()])
        var_name = match.group(1)
        expr = match.group(2) or '[^/]+'
        expr = '(?P<%s>%s)' % (var_name, expr)
        regex += expr
        last_pos = match.end()
    regex += re.escape(template[last_pos:])
    regex = '^%s$' % regex
    return regex

class Router(object):
    def __init__(self, _routes=[] ):
        self.routes = _routes

    def add(self, template, controller, **vars):
        self.routes.append((re.compile(template_to_regex(template)),
                            controller, vars))
    
    def __call__(self, environ, start_response):
        """ Falta el codigo que implementa """
        """ el anexo en el request de las  """
        """ variables en la url de regex.  """
        req = Request(environ)
        for regex, ctrl, vars in self.routes:
            match = regex.match(req.path_info)
            if match:
                req.urlvars = match.groupdict()
                req.urlvars.update(vars)
                wsgi_ctrl = controller(ctrl) # controller_wrapper
                return wsgi_ctrl(environ, start_response)
        return exc.HTTPNotFound()(environ, start_response)

