Title: kafka监控web端(添砖)
Date: 2015-01-17 14:50
Modified: 2015-01-17 15:40
Category: Technology 
Tags: kafka,消息队列,监控
Slug: kafka_web_console
Author: ljingb

##前言
最近在了解消息队列,主要是之前用的是redis,redis固然非常好用,但是也有相应的使用场景.随着数据量的增长,redis已经不能满足现在的需求了.所以需要找个更好的替代品.问了一圈大牛,也google一番,锁定在[kafka](http://kafka.apache.org/)上了.关于**kafka**怎么"玩",我也不知道,算是在摸索当中,想要知道安装使用等方法,请移步Google吧.虽然kafka我不会玩,但是我会玩怎么监控它.

* * *

##简介
> 
> [kafka-web-console](https://github.com/claudemamo/kafka-web-console),是kafka自己的一个Web管理界面.开源的东西好是好,但是不知道是不是开源的大牛B们都不愿意写文档!!出来个东西,居然没有安装步骤,只是有一些简单的使用说明,甚至说明都不详细,对于此点表示很坑!

* * *

##安装
>
> ##### 1.先下载安装scala构建工具[sbt](http://www.scala-sbt.org/0.13/tutorial/Installing-sbt-on-Linux.html)
> 
```
 #本安装环境为centos6.5
 curl https://bintray.com/sbt/rpm/rpm > bintray-sbt-rpm.repo
 sudo mv bintray-sbt-rpm.repo /etc/yum.repos.d/
 sudo yum install sbt
```
>
> ##### 2.下载**kafka-web-console**
>
> ```
 git clone https://github.com/claudemamo/kafka-web-console  
> ```
>
> ##### 3.构建包
```
cd kafka-web-console/  
sbt dist
```
> 此处是构建出一个可用的standalone包来,以后用的话直接部署使用即可.另外,网上有写教程有说需要设置下数据库等设置,看着有些麻烦,默认的数据库是H2,我没有设置其他的数据库,以我的成功案例来看,此处保持默认设置即可.

> 补充:其实早就相对GFW说生祝福了,用sbt构建包的时候问题多多,主要都是下载相关依赖的问题.好多依赖已经被墙了,以至于下载巨慢无比,甚至下载失败.有此问题的请挂代理.sbt怎么设置代理?你问我,我也不会,但是总有人会,请异步--->[sbt构建代理设置](http://stackoverflow.com/questions/13803459/how-to-use-sbt-from-behind-proxy)
>
> ##### 4.部署运行
> 当你顺利的构建完成之后,在```kafka-web-console/target/universal```下出先一个压缩包.此压缩包正是刚才编译出的应用端.解压zip即可.
```
unzip kafka-web-console-2.1.0-SNAPSHOT.zip  
cd kafka-web-console-2.1.0-SNAPSHOT/bin
#第一次启动加个参数不然报错
./kafka-web-console -DapplyEvolutions.default=true
```
> 至此你可以访问相应的机器的9000端口就可以体验了.
> 
> ##### 查看帮助以及后台运行
```
./kafka-web-console -h  
nohup ./kafka-web-console >/dev/null 2>&1 &
```
* * *
##总结
其实关于kafka相关的知识相当匮乏,林林总总的通过各种博客看了一些简介,摸着石头过河.后续有对kafka的研究再进行记录了解.
