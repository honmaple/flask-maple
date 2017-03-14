#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: _compat.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-12-11 23:42:23 (CST)
# Last Update:星期一 2016-12-12 0:46:56 (CST)
#          By:
# Description:
# **************************************************************************
from flask_babelex import Domain
from flask_maple import translations

translations = translations.__path__[0]
domain = Domain(translations)

gettext = domain.gettext
ngettext = domain.ngettext
lazy_gettext = domain.lazy_gettext
