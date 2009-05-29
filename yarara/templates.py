from jinja import Environment, FileSystemLoader
import config

def render(template, vars):
    _environment = Environment(loader=FileSystemLoader(config.templates))
    tmpl = _environment.get_template(template)
    return tmpl.render(vars)

