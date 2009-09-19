"""

Copyright (c) 2009, Marcelo Alaniz.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the Marcelo Alaniz nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY Marcelo Alaniz''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL <copyright holder> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""


#import sys, os
import mimetypes
import re
import os
import sys
import urlparse
import cgi


class Ya(object):
  def __init__(self, configuration=None):
    global _hub
    if _hub is not None:
      _hub = None
      print >>sys.stderr, 
    else: _hub = self
    self.routes = []
    self.find_user_path()
    # begin default configuration --------------------------
    self.config = {
      # meta configuration
      'log': True,
      'routes': self.routes,
      'self': self,
      # types and encondings
      'charset': 'utf-8',
      'content_type': 'text/html',
      # server options
      'mode': 'dev',
      'dev_port': 8080,
      # static files
      'use_static': True,
      'static_url': '/static/*:file/',
      'static_root': os.path.join(self.app_path, 'static/'),
      'static_handler': static_serve,
      # template options
      'use_templates': False,
      'template_lib': 'jinja2',
      'get_template_handler': _get_template_handler,
      'render_template_handler': _render_template_handler,
      'auto_reload_templates': True,
      'translations': [],
      'template_kwargs': {},
      #'template_root': os.path.join(self.app_path, 'templates/'),
      'template_root': 'templates/',
      '404_template': '404.html', #not found
      '500_template': '500.html', #server error
      # database options
      'use_db': False,
      'db_type': 'sqlite',
      'db_location': ':memory:',
      'db_models': {},
      # session options
      'use_sessions': False,
      'session_lib': 'beaker',
      # debugger
      'use_debugger': False,
      'raise_view_exceptions': False,
      # Custom Middleware
      'middleware': []
    } # end default configuration --------------------------
    if configuration is not None: self.config.update(configuration)
    if self.config['use_static']:
      self.setup_static()
    if self.config['use_templates']:
      self.setup_templates()
    if self.config['use_db']:
      self.setup_database()

  def find_user_path(self):
    try:
      raise Exception
    except:
      traceback = sys.exc_info()[2]
      if traceback is None:
        print >>sys.stderr, 'Warning: Failed to find current working directory.'
        print >>sys.stderr, '         Default static_root and template_root'
        print >>sys.stderr, '         values may not work correctly.'
        filename = './'
      else:
        frame = traceback.tb_frame
        while traceback is not None:
          if frame.f_back is None:
            break
          frame = frame.f_back
        filename = frame.f_code.co_filename
    self.app_path = os.path.abspath(os.path.dirname(filename)) #esto no sirve
    #self.app_path = os.path.abspath(os.path.dirname(__file__))

  def setup_static(self):
    self.route(self.config['static_url'], self.config['static_handler'], '*')

  def setup_templates(self):
    if self.config['template_lib'] == 'jinja2':
      import jinja2
      # If the user specified translation objects, load i18n extension
      if len(self.config['translations']) != 0:
        extensions = ['jinja2.ext.i18n']
      else:
        extensions = ()
      self.config['template_env'] = jinja2.Environment(
        loader  = jinja2.FileSystemLoader(
            searchpath = self.config['template_root'],
            encoding   = self.config['charset'],
        ),
        auto_reload = self.config['auto_reload_templates'],
        extensions = extensions,
        **self.config['template_kwargs']
      )
      for translation in self.config['translations']:
        self.config['template_env'].install_gettext_translations(translation)
    if self.config['template_lib'] == 'mako':
      import mako.lookup
      self.config['template_env'] = make.lookup.TemplateLookup(
        directories = [self.config['template_root']],
        input_encoding = self.config['charset'],
        output_encoding = self.config['charset'],
        filesystem_checks = self.config['auto_reload_templates'],
        **self.config['template_kwargs']
      )
    if self.config['template_lib'] == 'appengine':
      from google.appengine.ext.webapp import template as gae_template
      #wrapper class for appengine
      class AppEngineTemplates(object):
        def __init__(self, searchpath):
          self.searchpath = searchpath

        def get_template(self, template):
          path = os.path.join(self.searchpath, template)
          return gae_template.load(path)
      self.config['template_env'] = AppEngineTemplates(
          self.config['template_root']) 


  def setup_database(self):
    # DB library imports
    from sqlalchemy import (create_engine, Table, MetaData, Column, Integer, 
                            String, Unicode, Text, UnicodeText, Date, Numeric, 
                            Time, Float, DateTime, Interval, Binary, Boolean, 
                            PickleType)
    from sqlalchemy.orm import sessionmaker, mapper
    # Create global name mappings for model()
    global column_mapping
    column_mapping = {'string': String,       'str': String,
                     'integer': Integer,      'int': Integer, 
                     'unicode': Unicode,     'text': Text,
                 'unicodetext': UnicodeText, 'date': Date,
                     'numeric': Numeric,     'time': Time,
                       'float': Float,   'datetime': DateTime,
                    'interval': Interval,  'binary': Binary,
                     'boolean': Boolean,     'bool': Boolean,
                  'pickletype': PickleType,
    }
    # Add a few SQLAlchemy types to globals() so we can use them in models
    globals().update({'Column': Column, 'Table': Table, 'Integer': Integer,
                      'MetaData': MetaData, 'mapper': mapper})
    # Ensures correct slash number for sqlite
    if self.config['db_type'] == 'sqlite':
      self.config['db_location'] = '/' + self.config['db_location']
      eng_name = self.config['db_type'] + '://' + self.config['db_location']
      self.config['db_engine'] = create_engine(eng_name)
      self.config['db_session'] = sessionmaker(bind=self.config['db_engine'])()

  def run(self, mode=None):
    """ run yararara in the set mode """
    if mode is None: mode = config('mode')
    else: config('mode', mode)
    # modes
    if   mode == 'dev'      : run_dev ('', config('dev_port'), self.request)
    elif mode == 'wsgi'     : return run_wsgi(self.request)
    elif mode == 'appengine': run_appengine(self.request)
    else: print >>stderr, "Error: unrecognized mode ... exiting."

  def request(self, request, method='*', **kwards):
    if config('log'): print "%s request for %s" %(method, request)
    req_obj = YaRequest(kwards)
    global _response
    _response = YaResponse()
    if request[-1] != '/': request += '/'
    for route in self.routes:
      if not route.match(request, method): continue
      if config('log'): 
        print '%s matches, calling %s() ...\n' % (route.old_url, 
            route.func.__name__)
      if config('raise_view_exception') or config('use_debugger'):
        response = route.dispatch(req_obj)
      else:
        try:
          response = route.dispatch(req_obj)
        except:
          return servererror(error=cgi.escape(str(sys.exc_info()))).render()
      if response is None: response = _response
      if isinstance(response, YaResponse):
        return response.render()
      return YaResponse(body=response).render()
    return notfound(error='No matching routes registered').render()

  def route(self, url, func, method):
    if url is None: url = '/' + func.__name__ + '/'
    if type(url) == str: 
      self.routes.append(YaRoute(url, func, method))
    else:
      for u in url: self.routes.append(YaRoute(u, func, method))

  def __getattr__(self, attr):
    if attr in self.config.keys():
      return self.config[attr]
    return None

  def __repr__(self): return '<Ya>'

class YaRoute(object):
  def __init__(self, url, func, method):
    if url[0] != '/': url = '/' + url
    if url[-1] != '/': url += '/'
    self.old_url = url
    splat_re = re.compile('^\*?:(?P<var>\w+)$')
    buffer = '^'
    for part in url.split('/'):
      if not part: continue
      match_obj = splat_re.match(part)
      if match_obj is None: buffer += '/' + part
      else: buffer += '/(?P<' + match_obj.group('var') + '>.*)'
    if buffer[-1] != ')': buffer += '/$'
    else: buffer += '/'
    self.url = re.compile(buffer)
    self.func = func
    self.method = method.upper()
    self.params = {}

  def match(self, request, method):
    match_obj = self.url.match(request)
    if match_obj is None: return False
    if self.method != '*' and self.method != method: return False
    self.params.update(match_obj.groupdict())
    return True

  def dispatch(self, req):
    return self.func(req, **self.params)

  def __repr__(self):
    return '<YaRoute: %s %s - %s()>' %(self.method, self.old_url, 
        self.func.__name__)

class YaRequest(object):
  def __init__(self, request):
    if 'DOCUMENT_URI' not in request: request['DOCUMENT_URI'] = '/'
    elif request['DOCUMENT_URI'][-1] != '/': request['DOCUMENT_URI'] += '/'
    self.raw = request
    self.raw['input'] = {}
    self.location = request['DOCUMENT_URI']
    if 'REQUEST_URI' in request: self.full_location = request['REQUEST_URI']
    else: self.full_location = self.location
    if 'HTTP_USER_AGENT' in request: 
      self.user_agent = request['HTTP_USER_AGENT']
    elif 'User-Agent' in request:
      self.user_agent = request['User-Agent']
    else:
      self.user_agent = ''
    self.combine_request_dicts()
    if config('use_sessions') and config('session_lib') == 'beaker':
      self.session = request['beaker.session']
    else:
      self.session = None

  def combine_request_dicts(self):
    input_dict = self.raw['QUERY_DICT'].copy()
    for k, v in self.raw['POST_DICT'].items():
      if k in input_dict.keys(): input_dict[k].extend(v)
      else: input_dict[k] = v
    for k, v in input_dict.items():
      if len(v) == 1: input_dict[k] = v[0]
    self.raw['input'] = input_dict

  def __getattr__(self, attr):
    if attr in self.keys(): return self.raw[attr]
    return none

  def input(self, arg=None):
    if arg is None: return self.raw['input']
    if self.raw['input'].has_key(arg):
      return self.raw['input'][arg]
    return None
  
  def __getitem__(self, key): return self.raw[key]
  def __setitem__(self, key, val): self.raw[key] = val
  def keys(self): return self.raw.keys()
  def items(self): return self.raw.items()
  def values(self): return self.raw.values()
  def __len__(self): return len(self.raw)
  def __contains__(self, key): return key in self.raw

  def __repr__(self):
    return '<YaRequest: %s>' % self.location

class YaResponse(object):
  status_codes = {
    200: 'Ok',
    301: 'Moved permanently',
    302: 'Found',
    303: 'See Other',
    304: 'Not modified',
    400: 'Bad request',
    403: 'Forbidden',
    404: 'Not found',
    405: 'Method not allowed',
    410: 'Gone',
    500: 'Internal server error'
  }

  def __init__(self, configuration=None, **kwards):
    self.config = {
      'body': '',
      'status': 200,
      'headers': { 'Content-Type': config('content_type'), },
    }
    if configuration is None: configuration = {}
    self.config.update(configuration)
    self.config.update(kwards)
    self.config['headers']['Content-Length'] = len(self.config['body'])

  def append(self, text):
    self.config['body'] += str(text)
    self.config['headers']['Content-Length'] = len(self.config['body'])
    return self

  def __iadd__(self, text):
    return self.append(text)

  def render(self):
    """ Return 3-tuple (status_string, headers, body). """
    status_string = '%s %s' %(self.config['status'], 
      self.status_codes[self.config['status']])
    headers = [(k, str(v)) for k, v in self.config['headers'].items()]
    body = '%s' % self.config['body']
    return (status_string, headers, body)

  def header(self, header, value):
    self.config['headers'][header] = value
    return self

  def __setitem__(self, header, value): self.header(header, value)
  def __getitem__(self, header): return self.config['headers'][header]
  def __getattr__(self, attr): return self.config[attr]
  def __repr__(self): return '<YaResponse: %s %s>' %(self.status, 
      self.status_codes[self.status])
  

_hub = None

def init(configuration=None):
  global _hub
  if _hub is None:
    _hub = Ya(configuration)
  return _hub

def config(key, value=None):
  if _hub is None: init()
  if value is None:
    if type(key) == dict: _hub.config.update(key)
    else:
      if key in _hub.config.keys():
        return _hub.config[key]
      return None
  else: _hub.config[key] = value

def run(mode=None):
  if _hub is None: init()
  if len(sys.argv) > 1:
    if '-mode=' in sys.arg[1]: mode = sys.argv[1].split('=')[1]
    elif '-mode' == sys.arg[1]: mode = sys.argv[2]
  return _hub.run(mode)

#
# decorators
#
def route(url=None, method='*'):
  if _hub is None: init()
  def wrap(f): _hub.route(url, f, method)
  return wrap

def post(url=None):   return route(url, 'post')
def get(url=None):    return route(url, 'get')
def head(url=None):   return route(url, 'head')
def put(url=None):    return route(url, 'put')
def delete(url=None): return route(url, 'delete')


#
#   Functions to deal with the global response object (_response)
#

_response = None

def append(body):
    """Add text to response body. """
    global _response
    return _response.append(body)

def header(key, value):
    """Set a response header. """
    global _response
    return _response.header(key, value)

def content_type(type):
    """Set the content type header. """
    header('Content-Type', type)

def status(code):
    _response.config['status'] = code


#
#   Convenience functions for 404s and redirects
#

def redirect(url, code=302):
    status(code)
    # clear the response headers and add the location header
    _response.config['headers'] = { 'Location': url }
    return _response

def assign(from_, to):
    if type(from_) not in (list, tuple): from_ = [from_]
    for url in from_:
      @route(url)
      def temp(web): redirect(to)

def notfound(error='Unspecified error', file=None):
    """Sets the response to a 404, sets the body to 404_template."""
    if config('log'): print >>sys.stderr, 'Not Found: %s' % error
    status(404)
    if file is None: file = config('404_template')
    return template(file, error=error)

def servererror(error='Unspecified error', file=None):
    """Sets the response to a 500, sets the body to 500_template."""
    if config('log'): print >>sys.stderr, 'Error: (%s, %s, %s)' % sys.exc_info()
    status(500)
    if file is None: file = config('500_template')
    # Resets the response, in case the error occurred as we added data to it
    _response.config['body'] = ''
    return template(file, error=error)

#
#   Serve static files.
#

def static_serve(web, file):
    """The default static file serve function. Maps arguments to dir structure."""
    file = os.path.join(config('static_root'), file)
    print "file: %s " % file
    realfile = os.path.realpath(file)
    if not realfile.startswith(config('static_root')):
      notfound("that file could not be found/served")
    elif yield_file(file) != 7:
      notfound("that file could not be found/served")


def yield_file(filename, type=None):
    """Append the content of a file to the response. Guesses file type if not
    included.  Returns 1 if requested file can't be accessed (often means doesn't 
    exist).  Returns 2 if requested file is a directory.  Returns 7 on success. """
    if not os.access(filename, os.F_OK): return 1
    if os.path.isdir(filename): return 2
    if type is None:
      guess = mimetypes.guess_type(filename)[0]
      if guess is None: content_type('text/plain')
      else: content_type(guess)
    else: content_type(type)
    append(open(filename, 'r').read())
    return 7

#
#   Templating
#

def template(template_path, template_dict=None, **kwargs):
  """Append a rendered template to response.  If template_dict is provided,
  it is passed to the render function.  If not, kwargs is."""
  # Retreive a template object.
  t = get_template(template_path)
  # Render it without arguments.
  if not kwargs and not template_dict: 
    return append(render_template(t))
  # Render the template with a provided template dictionary
  if template_dict: 
    return append(render_template(t, **template_dict))
  # Render the template with **kwargs
  return append(render_template(t, **kwargs))

def get_template(template_path):
  """Returns a template object by calling the default value of
  'get_template_handler'.  Allows getting a template to be the same
  regardless of template library."""
  if config('use_templates'):
    return config('get_template_handler')(template_path)
  else: return "caca" 


# The default value of config('get_template_handler')
def _get_template_handler(template_path):
  """Return a template object.  This is defined for the Jinja2 and
  Mako libraries, otherwise you have to override it.  Takes one 
  parameter: a string containing the desired template path.  Needs
  to return an object that will be passed to your rendering function."""
  if config('use_templates'):
    return config('template_env').get_template(template_path)
  else: return None

def render_template(template_obj, **kwargs):
  """Renders a template object by using the default value of
  'render_template_handler'.  Allows rendering a template to be consistent
  regardless of template library."""
  if config('use_templates'):
    #print config('render_template_handler')(template_obj, **kwargs)
    return config('render_template_handler')(template_obj, **kwargs)
  else: return None

# The default value of config('render_template_handler')
def _render_template_handler(template_obj, **kwargs):
  """Renders template object with an optional dictionary of values.
  Defined for Jinja2 and Mako - override it if you use another
  library.  Takes a template object as the first parameter, with an
  optional **kwargs parameter.  Needs to return a string."""
  if config('template_lib') == 'mako': return template_obj.render(**kwargs)
  if config('template_lib') == 'jinja2':
    # Jinja needs its output encoded here
    return template_obj.render(**kwargs).encode(config('charset'))
  if config('template_lib') == 'appengine':
    from django.template import Context
    return template_obj.render(Context(kwargs))

def autotemplate(urls, template_path):
  """Automatically renders a template for a given path.  Currently can't
  use any arguments in the url."""
  if type(urls) not in (list, tuple): urls = urls[urls]
  for url in urls:
    @route(url)
    def temp(web): template(template_path)
    


#
# data modeling
#

class YaModelMetaClass(type):
  def __new__(cls, name, bases, dct):
    return type.__new__(cls, name, bases, dct)
  def __init__(cls, name, bases, dct):
    super(YaModelMetaClass, cls).__init__(name, bases, dct)

column_mapping = {}
session = lambda: config('db_session')

def model(model_name, **kwargs):
  if not _hub: init()
  def __init__(self, **kwargs):
    for k, v in kwargs.items():
      self.__dict__[k] = v
  def add(self):
    session.add(self)
    return self
  def save(self):
    s = session()
    if self not in s: s.add(self)
    s.commit()
    return self

  def __repr__(self):    return u'<%s: id=%s>' % (self.__name__, self.id)
  def __str__(self):    return '<%s: id=%s>' % (self.__name__, self.id)
  def __unicode__(self): return u'<%s: id=%s>' % (self.__name__, self.id)

  def find_f(cls):
    return session().query(cls)

  cls_dict = {
    '__init__': __init__,
    'add': add,
    'save': save,
    '__name__': model_name,
    '__repr__': __repr__,
    '__str__' : __str__,
    'find': None,
  }

  cols = [ Column('id', Integer, primary_key=True), ]
  for k, v in kwargs.items():
    if callable(v):
      cls_dict[k] = v
    elif isinstance(v, Column):
      if not v.name: v.name = k
      cols.append(v)
    elif type(v) == str:
      v = v.lower()
      if v in column_mapping: v = column_mapping[v]
      else: raise NameError("'%s' is not an allowed database column" % v)
      cols.append(Column(k, v))

  t = YaModelMetaClass(model_name, (object, ), cls_dict)
  # need a object instance
  t.find = staticmethod(lambda: find_func(t))
  # now we create the class
  metadata = MetaData()
  t_tbl = Table(model_name +'s', metadata, *cols)
  metadata.create_all(config('db_engine'))
  mapper(t, t_tbl)
  config('db_models')[model_name] = t
  return t

def find(model_cls):
  if type(model_cls) == str:
    try: model_cls = models[model_cls]
    except: raise NameError("No such model exists ('%s')" % model_cls)
  return session().query(model_cls)



def get_application(process_func):
  def app(environ, start_response):
    if environ is None:
      print >>sys.stderr, 'Error: environ is None for some reason'
      sys.exit()
    # ensume some variable exist. (WSGI don't guarantee them)
    if 'PATH_INFO' not in environ.keys() or not environ['PATH_INFO']:
      environ['PATH_INFO'] = '/'
    if 'QUERY_STRING' not in environ.keys():
      environ['QUERY_STRING'] = ''
    if 'CONTENT_LENGTH' not in environ.keys() or not environ['CONTENT_LENGTH']:
      environ['CONTENT_LENGTH'] = '0'
    #standarize some header names
    environ['DOCUMENT_URI'] = environ['PATH_INFO']
    if environ['QUERY_STRING']:
      environ['REQUEST_URI'] = environ['PATH_INFO']+'?'+environ['QUERY_STRING']
    else:
      environ['REQUEST_URI'] = environ['DOCUMENT_URI']
    # parse query string
    environ['QUERY_DICT'] = cgi.parse_qs(environ['QUERY_STRING'], 
      keep_blank_values=1)
    if environ['REQUEST_METHOD'] in ('POST', 'PUT'):
      fs = cgi.FieldStorage(fp=environ['wsgi.input'],
          environ=environ, keep_blank_values=True)
      post_dict = {}
      if fs.list:
        for field in fs.list:
          if field.filename: value = field
          else: value = field.value
          # all arguments are list always
          if not field.name in post_dict:
            post_dict[field.name] = [value]
          else:
            post_dict[field.name].append(value)
      environ['POST_DICT'] = post_dict
    else: environ['POST_DICT'] = {}
    # the environ it's right! now call to yarara
    status_str, headers, body = process_func(
        environ['PATH_INFO'], environ['REQUEST_METHOD'], **environ)
    start_response(status_str, headers)
    return [body]
  middleware_list = []
  if config('use_sessions') and config('session_lib') == 'beaker':
    middleware_list.append(('beaker.middleware.SessionMiddleware', {}))
  middleware_list.extend(config('middleware'))
  app = _load_middleware(app, middleware_list)
  return app

def _load_middleware(app, middleware_list):
  for middleware, args in middleware_list:
    parts = middleware.split('.')
    module = '.'.join(parts[:-1])
    name = parts[-1]
    try:
      obj = getattr(__import__(module, None, None, [name]), name)
      app = obj(app, **args)
    except (ImportError, AttributeError):
      print 'Warning: failed to load middleware %s' % name
  return app

def run_dev(addr, port, process_func):
  from wsgiref.simple_server import make_server
  app = get_application(process_func)
  print ''
  print "   _     _                                "
  print "   ( )   ( )                              "
  print "   `\`\_/'/'_ _  _ __   _ _  _ __   _ _   "
  print "     `\ /'/'_` )( '__)/'_` )( '__)/'_` )  "
  print "      | |( (_| || |  ( (_| || |  ( (_| |  "
  print "      (_)`\__,_)(_)  `\__,_)(_)  `\__,_)  "
  print ''
  print 'Runing Yarara development server, <C-c> to exit...'
  print 'connect to 127.0.0.1:%s and use your web app' % port
  print ''
  srv = make_server(addr, port, app)
  try:
    srv.serve_forever()
  except:
    print 'Interrupted; yarara it is down...'
    srv.socket.close()

def run_appengine(process_func):
  from google.appengine.ext.webapp.util import run_wsgi_app
  return run_wsgi_app(get_application(process_func))
  #from google.appengine.ext import webapp
  #application = webapp.WSGIApplication([('/', get_application(process_func))], debug=True)
  #run_wsgi_app(get_application(application) ) 



