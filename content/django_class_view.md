Title: django之基于Class-View定制统一API
Date: 2016-04-18 18:40
Modified: 2016-05-14 23:00
Category: Technology
Tags: python,django,django view
Slug: django_class_view
Author: ljingb

近期部门启动了一个"朝阳"项目,从项目规划选型到完成初版披荆斩棘,今仅对项目中用到的知识点作总结,如果项目发展顺利,后期再继续分享我们的"朝阳"项目更多细节.
## 0x01 Django框架
django用来开发内部的运维系统和支持系统个人认为是个不错的选择.你有权力说其他语言,其他框架,我也有权利保持沉默,暂且不挑起语言之争(其实php是世界上最好的语言.^_^).
Django严格来说是一个MTV框架,结构与传统MVC架构没有太大的区别.它的核心包含以下几部分:

 1. Model层,一个对象关系映射,作为数据模型和关系型数据库的媒介,对数据的封装简直太友好了
 2.  URL(Controller)层.一个基于正则表达式的URL分发器
 3.  View层,一个用于处理HTTP请求的系统和web模版渲染系统

另外Django的一个好处就是模块化设计,每一个模块在内部都称之为APP,在每个APP里面都有自己的三层结构.
如图:

![django_app_arch](/pictures/django_app_arch.jpg u"django_app_arch")

模块化后,不仅可以在开发的时候更容易理解系统,而且因为每个APP都是独立的应用,可以尽量的减少系统的耦合,便于系统后续的扩展和维护.

ps: 个人认为脚本语言+框架开发是映射现在互联网风的,快速迭代,小步快跑,为快不破,对于臃肿的语言+自己写框架来说更胜一筹. 

## 0x02 Class-View
之前使用django开发系统都是使用 `func-view`, `func-view` 在小规模系统或是一个人开发的时候使用还是可以,但是到中大型项目中,多人协作开发后很容易出现标准和开发风格不统一的问题(当然还有其他问题).
Django 还有一种视图 `class-view`,用类是为了抽象,抽象出通用的,将可变的暴露出来,这样可以提高代码的复用.对比 `func-view` 的优势:

 - 对HTTP方法的(GET/POST等)扩展,以及其他HTTP方法,请求不通过if判断解决
 - 可以通过继承内建通用视图,覆盖其中的方法,属性等,实现自己想要的功能,抽象通用功能
 - 在项目中可以统一调用API底层规范,更加灵活扩展

Django 的URL解析器是将请求映射到指定的函数而不是一个类,所有XXXView类(ListView/DetailView)有一个共同的父类: `View` ,在这个父类中,向外暴露了一个方法: `as_view()`,用来作为类的可调用入口.

```
from django.conf.urls import patterns
from django.views.generic import TemplateView

urlpatterns = patterns('',
    (r'^about/', TemplateView.as_view(template_name="about.html")),
)
```

`as_view()` 创建类的实例并调用 `dispatch()` 方法来查看请求是 `GET` 还是 `POST` 以及其他什么请求,并将请求转发到对应的方法,

## 0x03 封装API统一入口
对于一个工程来讲,API需要有统一的认证,统一的数据格式返回,可以利用Class-View来自己封装一个所有API接口的基础类

```
"所有API接口的基础类"
class CoreView(JSONResponse, View):
    '''
    所有API基类
    '''
    def parameters(self, key):
        '''
        获取POST或者GET中的参数
        '''
        if self.request.method == 'GET':
            return self.request.GET.get(key)
        if self.request.method == 'POST':
            if key in json.loads(self.request.body.decode('utf-8')):
                return json.loads(self.request.body.decode('utf-8')).get(key)
            else:
                return ''
                
    def get(self, request, *args, **kwargs):
        '''
        收到GET请求后的处理
        '''
        if 'action' not in kwargs:
            return JSONResponse.invalid(self)

        action = 'get_%s' % kwargs['action'].lower()
        return self.run(action, request)

    def post(self, request, *args, **kwargs):
        '''
        收到POST请求后的处理
        '''
        if 'action' not in kwargs:
            return JSONResponse.invalid(self)

        action = 'post_%s' % kwargs['action'].lower()

        return self.run(action, request)

    def run(self, action, request):
        '''
        执行相应的逻辑
        '''
        self.request = request

        try:
            func = getattr(self, action)
        except:
            return JSONResponse.invalid(self)

        try:
            context = func()
        except APIError, e:
            return JSONResponse.fail(self, e.code, e.message)

        return JSONResponse.success(self, context)
```

View 调用:

```
Class Search(CoreView):
    def get_byid(self):
	    do something ....
		return data
	
	def post_update(self):
	    do something ....
	    return data
```

URL 解析

```
from django.conf.urls import patterns, include, url
import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = patterns('api',
    url(r'^(?i)api/search/(?P<action>\w+)/$', csrf_exempt(views.Search.as_view())),
)
```

API 请求:

```
GET http://127.0.0.1:8000/api/search/byid/

POST http://127.0.0.1:8000/api/serarch/update/
```

当然,想做到统一,还需要在 `CoreView` 中封装好统一的返回 `code` 以及 `message` 和 `data` 格式来做统一API响应规范.作为后续扩展,还可以继续添加公共方法,以做抽象.

## 0x04 关于视图
视图的扩展和解析还涉及到很多内容,但是大致思想和基类基本一致,更多内容可以参考:

* http://blog.csdn.net/hackerain/article/details/40919789
* http://pylixm.cc/posts/2016-03-24-Django-class-Views.html
* http://python.usyiyi.cn/django_182/index.html