import os, sys

# current woring directory
ROOT_PATH = os.path.dirname(__file__)

# python to yarara dev
sys.path += [ os.path.join(ROOT_PATH, '../../') ]

# elixir metadata
metadata = 'sqlite:///test.sqlite'

# server
host = 'localhost'
port = 8080

# path templates (absolute path)
templates = os.path.join(ROOT_PATH, 'tmpl')

# path to static files (like css, js and images files) (absolute path)
staticfiles = os.path.join(ROOT_PATH, 'static')


