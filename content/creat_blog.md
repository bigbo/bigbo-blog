Title: 用Pelican&GitHubPages搭建个人博客
Date: 2014-12-28 00:02
Modified: 2014-12-28 00:02
Category: Tecnology
Tages: github pages, pelican
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

> 1. 安装python
> 2. 安装git
> 3. 安装pip
> 4. 安装pelican&markdown    

    pip install pelican
    pip install markdown

####框架初建

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

####填写内容









