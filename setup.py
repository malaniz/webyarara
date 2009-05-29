#!/usr/bin/env python

from distutils.core import setup
setup(
    name='yarara',
    version='1.0',
    description='Yet Another Web Framework',
    author='Marcelo Alaniz',
    author_email='alanizmarcelo@gmail.com',
    url='http://www.yarara.net.ar',
    packages=['yarara', 'yarara.zero'],
    data_files=[
        ('/usr/bin', ['bin/ya'])
    ]

)

