Title: 用Pelican&GitHubPages搭建个人博客
Date: 2014-12-28 00:02
Modified: 2014-12-28 00:02
Category: Technology
Tags: github pages, pelican
Slug: create-blog
Author: ljingb

###前言
对于github.io早有认识,但是趋于各种懒,至今才动手.想把这几年的一些自己总结的东西做些记录,匆匆那些年,也应该给自己做些积累了.

那么问题来了,建立github page有各种框架,例如:[jekyll](http://jekyllrb.com/),[liquid](https://github.com/Shopify/liquid/wiki/Liquid-for-Designers),[Pelican](http://pelican-docs-zh-cn.readthedocs.org/en/latest/)等等,本文采用后者Pelican,关于Pelican不做过多介绍,想了解的就去连接到的文档看吧.

* * *

###搭建基础
Pelican基于Python,相比Wordpress等其他框架来说,它比较轻,另外有些自己的[特性](http://docs.getpelican.com/en/3.3.0/#features),再配合免费的github pages,非常棒!主要是在linux下进行搭建,过程中会涉及如下技术知识,不过都是很初级的使用,即使新手也可以很容易的上手.

> [github][1]
> 
> [github pages][2]
> 
> [git][3]
> 
> [python][4]
> 
> [pip][5]
> 
> [pelican][6]
> 
> [markdown][7]

  [1]: https://github.com
  [2]: https://pages.github.com
  [3]: http://git-scm.com/blog/2010/06/09/pro-git-zh.html
  [4]: http://www.python.org
  [5]: https://pypi.python.org/pypi/pip
  [6]: http://pelican-docs-zh-cn.readthedocs.org/en/latest
  [7]: http://wowubuntu.com/markdown/

* * *

###下载安装

由于是linux环境,大部分依赖是有的,没有的话可以通过yum/apt-get去安装.win的话就请参照安装.

> 1. 安装python (2.7+,低版本的不支持)
> 2. 安装git
> 3. 安装pip
> 4. 安装pelican&markdown    

    pip install pelican
    pip install markdown

- - -

###框架初建

创建文件夹,执行以下命令

    mkdir blog //注意命名
    cd blog
    pelican-quickstart

pelican-quickstart执行命令后,可以依照向导,输入相关配置项,怎么填写可以很随意,后续都可以在pelicanconf.py文件中进行更改.

命令成功执行后,会出现pelican的框架,如下所示:
    
    blog/
    |-- content             # 存放输入的markdown或RST源文件
    |-- output              # 存放最终生成的静态博客
    |-- pelicanconf.py      # 配置文件
    |-- develop_server.sh   # 测试服务器
    |-- Makefile            # 管理博客的Makefile
    `-- publishconf.py      # 发布文件，可删除

以上完成整体大的框架.

- - -

####填写内容

至此,我们可以开始使用Markdown创建一个页面,进入content文件夹,创建一个.md文件.大致如:

![Alt text](/pictures/pic1.png)

可以通过截图看到我现在这个页面的Markdown版本的源文件,这里要说的是开头部分的**Title,Category**等重点字段.详情见[文档](http://pelican-docs-zh-cn.readthedocs.org/en/latest/getting_started.html#pelican),涵义如下:

    Title: 文章标题
    Date: 创建日期
    Modified: 修改日期
    Category: 文章分类，标志本文处于该分类下
    Tags: 文章标签，标志本文处于该标签下
    Slug: URL中该文章的链接地址
    Author: 作者
    
可以简单的写个内容做测试,然后回到**blog**目录下.

执行**make html**生成html

    [jingbo.li@zero bigbo-blog]$ make html 
    pelican /home/jingbo.li/dev/bigbo-blog/content -o /home/jingbo.li/dev/bigbo-blog/output -s /home/jingbo.li/dev/bigbo-blog/pelicanconf.py 
    Done: Processed 1 article(s), 0 draft(s) and 1 page(s) in 0.83 seconds.
    
表示已经生成了html页面,可以去**/blog/output**目录下查看已经生成的html页面.

接着执行**make server**开启服务,可以看到相关log

    [jingbo.li@zero bigbo-blog]$ make serve 
    cd /home/jingbo.li/dev/bigbo-blog/output && python -m pelican.server

即可可以用浏览器访问**http://localhost:8000**看到显示效果.

**\*AD:更多便捷命令**

    make regenerate     #修改后自动创建静态界面(make html)
    make devserver      #相当于regenerate+serve
    make publish        #生成用于发布的html
    
文档中还有其他一些命令,请自行发掘.

* * *

###设置相关

- - -

####主题选择
如果你能到这一步,那么恭喜你,你已经搭建完一个属于自己的博客了.以下是对自己博客的包装.
首先打开[主题官网](http://www.pelicanthemes.com/)挑选自己喜欢的主题,当然我们可以把整个[主题库](https://github.com/getpelican/pelican-themes)clone到本地.

```

 git clone https://github.com/getpelican/pelican-themes.git

```

现在可以自由选择不错的主题了.打开**pelicanconf.py**配置文件,添加或是更改**THEME**为自己喜欢的主题.更多配置请见[官方文档](http://pelican-docs-zh-cn.readthedocs.org/en/latest/settings.html#id20).

例如选择notmyidea-cms-fr主题:

    THEME = 'pelican-themes/notmyidea-cms-fr' #相对路径或是绝对路径

* * *

#####link的图标不加载
主题选择后打开页面一看,擦,有些瑕疵,旁边的一些github等连接没有图片,影响美观不说B格瞬减.
连接上的小图标:

![如图上面的小图标](/pictures/pic2.png u"如图上面的小图标")

通过分析查看原因,得知是由于css问题,来到主题文件夹下,尝试修改加载的css文件:

```

  cd pelican-themes/notmyidea-cms-fr/static/css
  vim main.css
  #添加如下字段
  .social a[href*='github.com']:before {content: url('../images/icons/github.png'); margin-right: 2px; vertical-align: -3px;}
  #注意在相应位置放上图标

```

久违的图标就会展现在你的眼前了,B格瞬间上升几个百分点.

* * *

####添加评论系统
历经沧桑,终于算是大功告成.等下!貌似还缺一个功能,评论系统.评论可以促进交流,所以这个当然不能少了.目前采用的是国外的评论系统[Disqus](https://disqus.com/),安装流程注册填写,会给你博客相关站点分配一个**Shortname**.

回到配置文件**pelicanconf.py**添加配置

    DISQUS_SITENAME = Shortname

现在大功告成,可以生成页面开始把玩一番吧!

* * *

###编写文章

几经转辗,终于可以发篇文章炫耀下了,哈哈哈.本文给予**github pages**,当然如果你有自己的服务器可以根据[官方教程](https://help.github.com/articles/creating-pages-with-the-automatic-generator/)设置你自己的站点服务器.这样你就拥有一个二级域名和一个版本库.任性的更新.

进入***blog***目录下的***output***文件夹内,依次执行以下命令:

```

  git init
  git add .
  git remote add origin https://github.com/bigbo/bigbo.github.io
  git pull origin master
  git commit -m 'create blog'
  git push origin master

```

当然如果你不会git,没关系,现在先按照[官方文档](http://www.git-scm.com/book/zh/v1)敲就可以了.熟悉git的同学可以选择使用框架提供的**Makefile**文件进行一键上传.

一个完整的博客创建发布流程算是完成了.最后打开浏览器访问github pages的域名即可访问.

* * *

###总结
目前博客已经可以满足基本的正常使用了.其实我们还可以对其进行不断完善,让其变得更优雅.后续再写些关于插件\配置等有关的内容.

第一次建立属于自己的空间,写的过程中参见了网上不少的例子,内容都是参疵不齐.更多的是参照官方文档,或是请教[google](http://google.com),这个过程持续了3--4天,终于完成了第一篇,收获还是满满的.当然后续还会有第二第三篇.

不管怎样,收获远大于付出.也算是为2014画上半个句号.希望 2015 come on!





