#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'ljingb'
SITENAME = u'BigBo\'s blog'
SITEURL = u'http://bigbo.github.io/`'

PATH = 'content'

TIMEZONE = 'Asia/Shanghai'

DEFAULT_LANG = u'zh'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/%s.rss.xml'
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
FEED_DOMAIN = None
FEED_ATOM = None

## 博客连接
LINKS = (('Pelican Doc', 'http://pelican-docs-zh-cn.readthedocs.org/en/latest/'),
         (u'三斗室', 'http://chenlinux.com/'),
         ('JingY', 'http://argcv.com/'),
         ('Hailin Zeng', 'http://hailinzeng.github.io/'),)
         #('You can modify those links in your config file', '#'),)

## 社交连接
SOCIAL = (('atom', FEED_ALL_ATOM),
          ('GitHub', 'https://github.com/bigbo'),
          ('Google+', 'https://plus.google.com/109995827478386248705'),
          ('Linkedin', 'https://lnkd.in/bsndpJX'),)

## 分页
DEFAULT_PAGINATION = 10

## 静态目录设置
STATIC_PATHS = ["pictures", ]

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

## 主题设置
THEME = 'pelican-themes/notmyidea-cms-fr'
THEME_STATIC_DIR = 'theme'
CSS_FILE = "main.css"

## 评论设置
DISQUS_SITENAME = 'bigbo'

## 设置URL按照日期显示
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


## 插件目录
PLUGIN_PATHS = [u"pelican-plugins"]

PLUGINS = ["sitemap"]

## 配置sitemap 插件
SITEMAP = {
    "format": "xml",
    "priorities": {
        "articles": 0.7,
        "indexes": 0.5,
        "pages": 0.3,
    },
    "changefreqs": {
        "articles": "monthly",
        "indexes": "daily",
        "pages": "monthly",
    }
}

LICENSE = '转载请注明来源<a href="http://bigbo.github.io/" target="_blank">Bigbo</a>'


## 顶部菜单项
#MENUITEMS = [
#            ('archives',SITEURL+'/archives.html'),
#            ]

