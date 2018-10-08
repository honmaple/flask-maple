#!/usr/bin/env python
# -*- coding=UTF-8 -*-
# *************************************************************************
#   Copyright © 2015 JiangLin. All rights reserved.
#   Author:JiangLin
#   Mail:mail@honmaple.com
#   Created Time: 2016-03-28 15:52:43
#   Last Update: Wednesday 2018-09-26 10:52:50 (CST)
# *************************************************************************
import sys
import os


def babel_init():
    pybabel = 'pybabel'
    os.system(
        pybabel +
        ' extract -F babel.cfg -k lazy_gettext -o messages.pot ../flask_maple')
    os.system(pybabel +
              ' init -i messages.pot -d ../flask_maple/translations -l zh')
    os.unlink('messages.pot')


def babel_update():
    pybabel = 'pybabel'
    os.system(
        pybabel +
        ' extract -F babel.cfg -k lazy_gettext -o messages.pot ../flask_maple')
    os.system(pybabel +
              ' update -i messages.pot -d ../flask_maple/translations')
    os.unlink('messages.pot')


def babel_compile():
    pybabel = 'pybabel'
    os.system(pybabel + ' compile -d ../flask_maple/translations')


if len(sys.argv) < 2:
    print('help documention')
    sys.exit()

if sys.argv[1].startswith('--'):
    option = sys.argv[1][2:]
    if option == 'init':
        babel_init()
    elif option == 'update':
        babel_update()
    elif option == 'compile':
        babel_compile()
    else:
        print('error')
        sys.exit()
elif sys.argv[1].startswith('-'):
    option = sys.argv[1][1:]
    if option == 'i':
        babel_init()
    elif option == 'u':
        babel_update()
    elif option == 'c':
        babel_compile()
    else:
        print('error')
        sys.exit()
