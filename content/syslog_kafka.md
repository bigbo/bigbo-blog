Title: rsyslog与Kafka结合使用
Date: 2015-01-21 14:40
Modified: 2015-01-21 15:40
Category: Technology 
Tags: kafka,消息队列,rsyslog
Slug: syslog_kafka
Author: ljingb

##前言
最近在折腾[Rsyslog](http://www.rsyslog.com/),传输日志,对他怎么说呢,谁用谁知道,我仅仅是了解使用的程度,对于里面的坑以及使用策略还没有那么深入,不过日后会逐步的细化了解,其实现在对于日志传输来过网上一大堆技术方案任你选.但是感觉用rsyslog传输还是最方便,最快捷的.他以不变应万变,看图说话:

![rsyslog](/pictures/rsyslog_1.png u"rsyslog支持图")

可见rsyslog的覆盖面是相当的广泛.奈何近几日,打算把redis替换为[kafka](http://kafka.apache.org/),本篇主要记录`rsyslog`与`kafka`的对接使用. 上了.

* * *

##Rsyslog对kafka的支持
通过对[rsyslog官方文档](http://www.rsyslog.com/doc/master/configuration/modules/omkafka.html#example)查看,得知`rsyslog`对`kafka`的支持是`v8.7.0`版本后才提供的支持.通过[ChangeLog](https://github.com/rsyslog/rsyslog/blob/v8-stable/ChangeLog)也可以看出`V8.X`的版本变化.

查看本机的rsyslog版本:

```
rsyslog.x86_64                                      7.6.3-1.el6
```

先是升级.升级方式有多种,推荐使用[官方源用](http://www.rsyslog.com/rhelcentos-rpms/)`yum`方式升级.使用源升级后的稳定版目前最新的是`8.7.0-1.el6`,来查看下rpm包中是否包含`omkafka`这个插件.

```
# rpm -ql rsyslog
.......
/lib64/rsyslog/lmzlibw.so
/lib64/rsyslog/mmpstrucdata.so
.......
#主要看/lib64/rsyslog/目录下的.so文件
```
经过查看其实rpm包编译的版本中是不包含`kafka`的插件的.经过下载源码包查看,源码包中包含此模块,估计是rpm包编译的时候没有加入进去吧.所以选择自己编译这个模块,编译好了拷贝到相应目录.

下载源码包,使用`./configure -h`查看帮助信息.

```
  --enable-omkafka        Compiles omkafka module [default=no]
```

可以清楚的查看到其实这个模块默认是不开启的.所以自己编译加入这个模块,编译好会在相应目录产生`omkafka.so`这个文件,然后拷贝到`/lib64/rsyslog/`目录下即可.

* * *

##体验+设置
使用需要在`rsyslog.conf`配置文件下或是相应的配置文件中加入`module(load="omkafka")`表示引入该模块.测试使用可以参照[文档中的示例](http://www.rsyslog.com/doc/master/configuration/modules/omkafka.html#example).

其实文档是相当的简陋,使用示例感觉就是配置上仅仅能使用,更多更详细的根本没有介绍,索性[kafka官方的文档](http://kafka.apache.org/documentation.html#producerconfigs)是相当的详细.在使用的角度看,rsyslog目前是作为一个**Producer**的角色,所以可以依照kafka的文档的**3.3Producer Configs**章节设置,设置相应的参数可以放到`confParam`或是`topicConfParam`中就可以了.当然这个参数列表不是无限任何参数都可以往里面仍,根据rsyslog官方文档对这个参数的表述是:其实**omkafka**是使用`librdkafka`连接卡夫卡的,所以参数实际上那些`librdkafka`支持的参数.

仅仅测试的话,根据rsyslog官方文档中配置即可生效.更多的设置和方法还是参照kafka相关设置,以及经过自己充分测试再另行体验,由于我也是才接触配置,更多的使用也不太了解.没有文档真的很瞎啊,但是至少知道了大致怎么使用了.目前的体验来看`partitions.number`等参数是很好用的.

rsyslog的kafka模块使用[问答列表](http://lists.adiscon.net/pipermail/rsyslog/2014-December/039291.html)
