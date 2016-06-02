#!/usr/bin/env python
# -*- coding=UTF-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: flask_maple_login.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-04-16 22:17:32 (CST)
# Last Update:星期二 2016-5-31 0:5:5 (CST)
#          By: jianglin
# Description: use pillow generate captcha
# **************************************************************************
from random import sample, randint
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from flask import session
from io import BytesIO


class Captcha(object):
    def __init__(self, app=None):
        if app is not None:
            self.app = app
            self.init_app(self.app)
        else:
            self.app = None

    def init_app(self, app):
        self.captcha = app.config.get('CAPTCHA_URL', 'captcha')
        app.add_url_rule('/' + self.captcha, 'captcha', self.validate)

    def validate(self):
        t = GenCaptcha()
        buf = t.start()
        buf_value = buf.getvalue()
        response = self.app.make_response(buf_value)
        response.headers['Content-Type'] = 'image/jpeg'
        return response


class GenCaptcha(object):
    _letter_cases = "abcdefghjkmnpqrstuvwxy"
    _upper_cases = _letter_cases.upper()
    _numbers = ''.join(map(str, range(3, 10)))
    init_chars = ''.join((_letter_cases, _upper_cases, _numbers))
    fontType = "/usr/share/fonts/TTF/DejaVuSans.ttf"

    def create_validate_code(self,
                             size=(120, 30),
                             chars=init_chars,
                             img_type="GIF",
                             mode="RGB",
                             bg_color=(255, 255, 255),
                             fg_color=(0, 0, 255),
                             font_size=18,
                             font_type=fontType,
                             length=4,
                             draw_lines=True,
                             n_line=(1, 2),
                             draw_points=True,
                             point_chance=2):

        width, height = size
        img = Image.new(mode, size, bg_color)
        draw = ImageDraw.Draw(img)
        if draw_lines:
            self.create_lines(draw, n_line, width, height)
        if draw_points:
            self.create_points(draw, point_chance, width, height)
            strs = self.create_strs(draw, chars, length, font_type, font_size,
                                    width, height, fg_color)

        params = [1 - float(randint(1, 2)) / 100, 0, 0, 0,
                  1 - float(randint(1, 10)) / 100,
                  float(randint(1, 2)) / 500, 0.001,
                  float(randint(1, 2)) / 500]
        img = img.transform(size, Image.PERSPECTIVE, params)

        img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)

        return img, strs

    def create_lines(self, draw, n_line, width, height):
        '''绘制干扰线'''
        line_num = randint(n_line[0], n_line[1])  # 干扰线条数
        for i in range(line_num):
            # 起始点
            begin = (randint(0, width), randint(0, height))
            # 结束点
            end = (randint(0, width), randint(0, height))
            draw.line([begin, end], fill=(0, 0, 0))

    def create_points(self, draw, point_chance, width, height):
        '''绘制干扰点'''
        chance = min(100, max(0, int(point_chance)))  # 大小限制在[0, 100]

        for w in range(width):
            for h in range(height):
                tmp = randint(0, 100)
                if tmp > 100 - chance:
                    draw.point((w, h), fill=(0, 0, 0))

    def create_strs(self, draw, chars, length, font_type, font_size, width,
                    height, fg_color):
        c_chars = sample(chars, length)
        strs = ' %s ' % ' '.join(c_chars)  # 每个字符前后以空格隔开

        font = ImageFont.truetype(font_type, font_size)
        font_width, font_height = font.getsize(strs)

        draw.text(
            ((width - font_width) / 3, (height - font_height) / 3),
            strs,
            font=font,
            fill=fg_color)

        return ''.join(c_chars)

    def start(self):
        code_img = self.create_validate_code()
        buf = BytesIO()
        code_img[0].save(buf, 'JPEG', quality=70)
        session['captcha'] = code_img[1]
        return buf
