# -*- coding: utf-8 -*-

name = 'turret_resolver'

version = '1.1.3.0'

authors = ['wen.tan',
           'ben.skinner',
           'daniel.flood']

build_requires = ['python']

build_command = 'rez env python -c "python {root}/rezbuild.py {install}"'

requires = ['pgtk', 'tk_core']


def commands():
    env.PYTHONPATH.append('{root}/python')
    env.RESOLVE.set("{root}/bin/turret-resolver.bat")
    env.PATH.append('{root}/bin')
