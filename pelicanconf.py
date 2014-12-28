#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'ljingb'
SITENAME = u'BigBo\'s blog'
#SITEURL = 'http://bigbo.github.io'

PATH = 'content'

TIMEZONE = 'Asia/Shanghai'

DEFAULT_LANG = u'zh'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
FEED_DOMAIN = None
FEED_ATOM = None

# Blogroll
LINKS = (('Pelican Doc', 'http://pelican-docs-zh-cn.readthedocs.org/en/latest/'),
         (u'三斗室', 'http://chenlinux.com/'),
         ('JingY', 'http://argcv.com/'),)
         #('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (#('You can add links in your config file', '#'),
          ('GitHub', 'https://github.com/bigbo'),
          ('Google+', 'https://plus.google.com/109995827478386248705'),
          ('Linkedin', 'https://lnkd.in/bsndpJX'),)

DEFAULT_PAGINATION = 10

STATIC_PATHS = ["pictures", ]

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

THEME = 'pelican-themes/notmyidea-cms-fr'
THEME_STATIC_DIR = 'theme'
CSS_FILE = "main.css"

DISQUS_SITENAME = 'bigbo'

ARTICLE_URL = 'pages/{date:%Y}/{date:%m}/{date:%d}/{slug}/'
ARTICLE_SAVE_AS = 'pages/{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html'
PAGE_URL = 'pages/{slug}/'
PAGE_SAVE_AS = 'pages/{slug}/index.html'


NEWEST_FIRST_ARCHIVES = True

# code blocks with line numbers
PYGMENTS_RST_OPTIONS = {'linenos': 'table'}

# foobar will not be used, because it's not in caps. All configuration keys
# have to be in caps
foobar = "barbaz"

DISPLAY_TAGS_INLINE = True
DISPLAY_RECENT_POSTS_ON_SIDEBAR = True
