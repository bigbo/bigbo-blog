Title: Pelican设置及插件使用
Date: 2015-01-13 20:30
Modified: 2015-01-14 13:50
Category: Technology
Tags: github pages, pelican_plugin
Slug: blog_plugin
Author: ljingb

##前言
博客算是正式用起来了,觉得还不错,但是经过查看或是浏览其他人的博客,感觉自己的还是那么的low.为什么呢?因为没有选择一个高大上的主题,没有使用优秀的插件,没有做相关优化.查了查,还有好多后续工作要做.以下就对博客的插件等设置使用总结下.

* * *

##主题设置
简单粗暴的设置可以看[这里](http://bigbo.github.io/pages/2014/12/28/create-blog/)主题设置相关简介.但是我还想说,上面的那些设置还远远不够.

> 这里推荐一些优秀的主题
>
> * [Elegant](https://github.com/talha131/pelican-elegant),清俗淡雅.
>
> * [pelican-bootstrap3](https://github.com/DandyDev/pelican-bootstrap3),我早期用的一个主题,其中自己改了一些东西.此主题有些问题在于宽屏展示的会出现字体有宽边.
>
> * [pelican-fresh](https://github.com/jsliang/pelican-fresh).我现在使用的主题.各方面还都不错.
>
> 当然其实还有好多的优秀主题没有加入到[官方主题库](https://github.com/getpelican/pelican-themes),要善用github的搜索功能.

* * *

##插件设置
插件的使用会使你的博客增添一些好的功能.例如评论功能.这里我推荐一些不错值得装的插件.另外官方也有提供[插件库](https://github.com/getpelican/pelican-plugins).

> ####sitemap
> [sitemap](https://github.com/getpelican/pelican-plugins/tree/master/sitemap)可以生成xml和txt格式的网站地图,配置见插件的readme.
>
> ####gzip_cache
> [gzip_cache](https://github.com/getpelican/pelican-plugins/tree/master/gzip_cache),可以将所有的页面压缩为gz格式,相对来说能加快页面的加载速度.
>
> ####neighbors
> [neighbors](https://github.com/davidlesieur/multi_neighbors),邻居导航,也就是我们常说的上一篇下一篇文章
>
> ####related_posts
> [related_posts](https://github.com/LawrenceWoodman/related_posts-jekyll_plugin),相关文章,根据tags判断的
>
> 想使用当然还需要在配置文件**pelicanconf.py**中进行设置.例如:
```
## 插件目录
PLUGIN_PATHS = [u"pelican-plugins"]

PLUGINS = [u"sitemap",u"gzip_cache",u"neighbors",u"related_posts"]

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
```

* * * 

##加载慢的解决
当博客上传到github能正常访问后,你就会发现一个问题,加载太TMD慢了!还能不能让然正常的访问了!经过调试,发现是前端**css**资源需要加载[Google的字体服务](fonts.googleapi.com)时间过长导致.可以认定是GFW给封了.罪过罪过.

> ####解决方法
> * 1.下载字体文件,到网站的静态文件夹内,具体可以参考[让wordpress主题绕开对google的依赖](http://sudodev.cn/articles/354.html).不过此种方法也有些问题.把静态资源放到Github上加载时间也没别之前好多少.
> * 2.把Google的静态公共库替换为国内的公共库.例如我的给替换成[360的镜像地址](fonts.useso.com).其实这种方法也有些弊端,例如国外用户访问就会出现加载过慢的问题.但是毕竟我们在'朝内',所以就换成360的资源库吧.操作如下:

```
#static/css/目录下css文件中,例如main.css
@import url(//fonts.googleapi.com/css?family=Overlock:400,700,900);
@import url(//fonts.googleapi.com/css?family=PT+Mono);
#替换为
@import url(//fonts.useso.com/css?family=Overlock:400,700,900);
@import url(//fonts.useso.com/css?family=PT+Mono);
```
> 可以上传后测试下,基本上能在10s内刷新出来.效果明显.

**\*国内其他开公共库**:
 [百度CDN公共库][1]; 
 [新浪云计算CDN公共库][2]; 
 [又拍云JS库CDN服务][3]; 
 [七牛云静态文件CDN][4]; 

 [1]: http://developer.baidu.com/wiki/index.php?title=docs/cplat/libs
 [2]: http://lib.sinaapp.com/
 [3]: http://jscdn.upai.com/
 [4]: http://www.staticfile.org/ 

* * *

##Google(百度) Analytics和Webmasters设置
注册[Google Analytics](http://www.google.com/analytics/)和[Webmasters](http://www.google.com/webmasters/)可以更好的管理自己的站点,[百度站长工具](http://zhanzhang.baidu.com/)更好的让搜索引擎收录.认证有多种形式,可以根据注册使用向导来完成进一步设置.

* * *

##添加多说评论
首先在[多说](http://duoshuo.com/)的网站中注册一个账号.

> ####修改模板文件
> 修改```templates/article.html```内容,在最后一个endif之后添加如下内容
```
{% if DUOSHUO_SITENAME and SITEURL and article.status != "draft" %}
  <div class="comments">
    <h2>Comments !</h2>
    <!-- Duoshuo Comment BEGIN -->
    <div class="ds-thread"></div>
    <script type="text/javascript">
        var duoshuoQuery = {short_name:"{{ DUOSHUO_SITENAME }}"};
  (function() {
   var ds = document.createElement('script');
   ds.type = 'text/javascript';ds.async = true;
   ds.src = 'http://static.duoshuo.com/embed.js';
   ds.charset = 'UTF-8';
   (document.getElementsByTagName('head')[0]
    || document.getElementsByTagName('body')[0]).appendChild(ds);

   })();
  </script>
  <noscript>Please enable JavaScript to view the comments.</noscript>
<!-- Duoshuo Comment END -->
</endif>
```
> 这段代码会自动引入多说的评论插件,显示评论内容.
>
> ####修改配置文件
> 在Pelicanconf.py中添加
```
DUOSHUO_SITENAME = "你的blog名称"
```
> 然后重新生成网站就会看到相关的评论界面了.

* * * 

##配置文件其他配置
还有一些其他配置就不一一详解了,以下列出仅供参考.
```
## 设置URL按照日期显示
ARTICLE_URL = 'pages/{date:%Y}/{date:%m}/{date:%d}/{slug}/'
ARTICLE_SAVE_AS = 'pages/{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html'
PAGE_URL = 'pages/{slug}/'
PAGE_SAVE_AS = 'pages/{slug}/index.html'

## 分页
DEFAULT_PAGINATION = 2

## 静态目录设置
STATIC_PATHS = ["pictures", ]

## 顶部菜单项
MENUITEMS = [
            ('archives',SITEURL+'/archives.html'),
            ]
```

* * * 

##总结
以上算是对之前**创建静态博客**的补充.其实都算是基本的设置,其实还有好多的设置应该做些总结,例如:增加站内搜索框等.时间关系吧,随着对自己博客的改造逐渐进行补充.
