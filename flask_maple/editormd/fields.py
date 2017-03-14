#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: fields.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-12-02 15:51:48 (CST)
# Last Update:星期五 2016-12-2 20:48:36 (CST)
#          By:
# Description:
# **************************************************************************
from flask import url_for
from jinja2 import Markup
from flask import current_app
try:
    from html import escape
except ImportError:
    from cgi import escape
from wtforms.fields import TextAreaField
from wtforms.widgets import HTMLString, TextArea
from wtforms.compat import text_type
from wtforms.widgets.core import html_params


class _editormd(object):
    def __init__(self, cdn=False, static_file=None, config=None):
        self.cdn = cdn
        self.static_file = static_file
        self.config = config

    def editormdjs(self):
        path = url_for('static', filename='editormd/js/editormd.min.js')
        if self.static_file is not None:
            path = self.static_file + 'editormd/js/editormd.min.js'
        if self.cdn:
            pass
        return Markup('''
            <script type="text/javascript" src="%s"></script>
            ''' % path)

    def editormdcss(self):
        path = url_for('static', filename='editormd/css/editormd.css')
        if self.static_file is not None:
            path = self.static_file + 'editormd/css/editormd.css'
        if self.cdn:
            pass
        return Markup('''
        <link rel="stylesheet" href="%s" />
            ''' % path)

    def editormdlib(self):
        path = url_for('static', filename='editormd/lib/')
        if self.static_file is not None:
            path = self.static_file + 'editormd/lib/'
        return path

    def static(self):
        return self.editormdcss() + self.editormdjs()

    def html(self):
        editormd_html = '''
            <div id="%(formid)s">
                <textarea "%(fields)s">%(text)s</textarea>
            </div>
            <script type="text/javascript">
            var FlaskEditorMd;
            $(function() {
                FlaskEditorMd = editormd("%(formid)s", {
                    height  :  360,
                    syncScrolling : "single",
                    path    : "%(editormdlib)s",
                    placeholder:"",
                    toolbarIcons : function() {
                        return ["bold","del","italic","quote","uppercase","lowercase", "|",
                                "h1","h2","h3","h4","h5","|",
                                "list-ul","list-ol","hr","|",
                                "link","image","code","table","|",
                                "datetime","watch","preview","fullscreen","||",
                                "search","undo","redo"]
                    },
                });
            });
            </script>
        '''
        return editormd_html


class EditorMd(TextArea):
    def __call__(self, field, **kwargs):
        editormd = current_app.jinja_env.globals['editormd']
        kwargs.setdefault('id', field.id)
        editormd_html = editormd.html() % {
            'fields': html_params(
                name=field.name, **kwargs),
            'formid': field.id + '-editormd',
            'editormdlib': editormd.editormdlib(),
            'text': escape(
                text_type(field._value()), quote=False)
        }
        return HTMLString(editormd_html)


class EditorMdField(TextAreaField):
    widget = EditorMd()
