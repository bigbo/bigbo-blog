Title: MooseFS浅析(一)
Date: 2015-01-05 23:10
Modified: 2015-01-06 22:50
Category: Technology
Tags: 分布式文件系统,Moosefs,分布式存储
Slug: Moosefs_one
Author: ljingb

## 前言
之前面临大量数据存储问题,于是开始选择分布式文件系统.于是MooseFS便映入眼底.正好之前用过,所以直接拿来就用.光会用也不行,闲来之时对他进行了一些简单了解,不管是百度还是谷歌,搜到的都是零零散散的东西,更多的博客都是抄來抄去,所以打算自己做些整理,下面就我对MFS的认识进行一下总结.

* * *

## 简介
* MooseFS优越特性如下：
> 1. 高可用性(数据可以存储在多个机器上的多个副本)
> 2. 可动态扩展随时新增加机器或者是磁盘
> 3. 可回收在指定时间内删除的文件(“垃圾回收站”是一个系统级别的服务)
> 4. 可以对整个文件甚至在正在写入的文件创建文件的快照.
> 5. 使用和部署非常简单,直接mount使用

 对于 **Moosefs** 的介绍我在此就不详细说了,更多介绍可以查看 [官网][1] 以及 [英文版权威指南][2] 或是查看田逸所翻译总结的 [权威指南][3] ,以上介绍的比自己总结的可能更加详细.我后面的总结是对以上内容的补充.

** \*AD:更多资料详见[GitHub][4] **

[1]: http://www.moosefs.org/
[2]: http://www.moosefs.com/how_to_get.html
[3]: https://github.com/bigbo/tools/blob/master/study/mfs/MooseFS%E6%9D%83%E5%A8%81%E6%8C%87%E5%8D%97.pdf
[4]: https://github.com/bigbo/tools/tree/master/study/mfs

* * *

## 系统结构
* MFS文件系统结构包含4种角色:
> 1. 管理服务器managing server(master):负责各个数据存储服务器的管理,文件读写调度,文件空间回收以及恢复.多节点拷贝.单个机器管理整个文件系统,用来存储记录每一个文件的Metadata(记录文件的大小;文件的属性;文件的位置;也包括非规则文件的系统;如目录;sockets;管道和设备)
> 2. 元数据日志服务器Metalogger server(Metalogger):负责备份master服务器的变化日志文件,文件类型为changelog_ml.\*.mfs,以便于在master server出问题的时候接替其进行工作.
> 3. 数据存储服务器data servers (chunkservers):负责连接管理服务器,听从管理服务器调度,提供存储空间,并为客户提供数据传输.
> 4. 客户机挂载使用client computers:通过fuse内核接口挂接远程管理服务器上所管理的数据存储服务器,看起来共享的文件系统和本地unix文件系统使用一样的效果.

整体架构如图:

![MFS架构图](/pictures/mfs_pic3.png)

* * *

## 配置文件详解
> 主要对 **V1.6.27-5** 版本的配置文件进行解析,后续跟进 **2.x** 版本配置文件.

### master服务器
> Metadata元数据存储在master服务器的内存中,同时也保存在磁盘上(作为一个定期更新的二进制文件,并实时的更新changelog日志).如果存在metaloggers的话,主要的二进制文件以及日志也复制到metaloggers中.(权威手册中有详细性能测试信息)

#### master主要配置文件

* mfsmaster.cfg
> 主配置文件
```
参数说明如下：
 # WORKING_USER和WORKING_GROUP：是运行master server的用户和组；
 # SYSLOG_IDENT：是master server在syslog中的标识，也就是说明这是由master server产生的；
 # LOCK_MEMORY：是否执行mlockall()以避免mfsmaster 进程溢出(默认为0，即否)；
 # NICE_LEVE：运行的优先级(如果可以默认是 -19; 注意: 进程必须是用root启动)；
 # EXPORTS_FILENAME：被挂接目录及其权限控制文件的存放位置 
 # DATA_PATH：metadata files and lock file存放路径，此目录下大致有以下文件：metadata，changelog，sessions，stats，lock.
 # BACK_LOGS：metadata的change log文件数目(默认是 50);
 # BACK_META_KEEP_PREVIOUS = 1保留以前元文件数(默认是 1);
 # REPLICATIONS_DELAY_INIT：(initial delay in seconds before starting replications)初始延迟复制的时间(默认是300s);
 # REPLICATIONS_DELAY_DISCONNECT：(replication delay in seconds after chunkserver disconnection) chunkserver断开后复制延迟(默认是3600s)；
 # MATOML_LISTEN_HOST：用于metalogger连接的IP地址(默认是*,代表任何IP)；
 # MATOML_LISTEN_PORT：监听metalogger请求的端口地址(默认是9419)；
 # MATOCS_LISTEN_HOST：用于chunkserver连接的IP地址(默认是*，代表任何IP)；
 # MATOCS_LISTEN_PORT：监听chunkserver连接的端口地址(默认是9420)；
 # MATOCU_LISTEN_HOST：用于客户端挂接连接的IP地址(默认是*,代表任何IP)；
 # MATOCU_LISTEN_PORT：监听客户端挂载连接的端口地址(默认是9421)；
 # CHUNKS_LOOP_TIME ：(Chunks loop frequency in seconds)chunks的回环频率(默认是：300秒)；
 # CHUNKS_DEL_LIMIT：(Maximum number of chunks to delete in one loop)在一个loop中可以删除chunks的最大数 (默认：100)
 # CHUNKS_WRITE_REP_LIMIT：(Maximum number of chunks to replicate to one chunkserver in one loop)在一个loop里复制到一个chunkserver的最大chunk数目(默认是1)
 # CHUNKS_READ_REP_LIMIT：(Maximum number of chunks to replicate from one chunkserver in one loop)在一个loop里从一个chunkserver复制的最大chunk数目(默认是5)
 # REJECT_OLD_CLIENTS：弹出低于1.6.0的客户端挂接(0或1，默认是0)
```

* mfsexports.cfg

> MFS访问使用权限控制配置文件;地址可以指定的几种表现形式：

    所有ip，单个ip，IP网络地址/位数掩码，IP网络地址/子网掩码，ip段范围.

> 权限部分：
```
   ro  只读模式共享  
   rw  读写方式共享  
   alldirs  许挂载任何指定的子目录  
   maproot   映射为root,还是指定的用户   
   password  指定客户端密码
```

#### metadata.mfs文件
> metadata.mfs, metadata.mfs.back是MooseFS文件系统的元数据metadata的镜像,对集群的数据存储至关重要.做主从也好,做集群备份也好,都是对这些文件做的备份.

#### changelog.\*.mfs 文件
> 1. changelog.\*.mfs 是MooseFS文件系统元数据的改变日志(每一个小时合并到metadata.mfs中一次)
> 2. Metadata文件的大小取决于文件数(而不是他们的大小),Changelog的大小取决于每小时的操作次数.(mfsmaster.cfg配置文件中可以设置)

### metalogger服务器
> master备份服务器,在保证服务高可用的情况下使用(即使不做高可用也需要做个备份服务),服务器性能理论上要比master更好.至少不能比master次.

#### metalogger主要配置文件

* mfsmetalogger.cfg
```
 # WORKING_USER和WORKING_GROUP:是运行mfsmetalogger server的用户和组；
 # SYSLOG_IDENT :是mfsmetalogger server在syslog中的标识，也就是说明这是由mfsmetalogger server产生的；
 # LOCK_MEMORY:是否执行mlockall()以避免mfsmaster 进程溢出(默认为0，即否);
 # NICE_LEVEL：运行的优先级(如果可以默认是 -19; 注意: 进程必须是用root启动)；
 # DATA_PATH: metadata files and lock file存放路径，此目录下大致有以下文件：metadata，changelog，sessions，stats，lock.
 # BACK_LOGS：metadata的change log文件数目(默认是 50);

 # META_DOWNLOAD_FREQ = 1 #metadata元数据下载间隔时间(默认是24小时，单位是小时，至多是BACK_LOGS的1/2)
 # MASTER_RECONNECTION_DELAY = 5   # 在失去连接之后延迟多少秒重新连接master
 # MASTER_HOST = MASTERMFS # master的HOST地址
 # MASTER_PORT = 9419
 # MASTER_TIMEOUT = 60 # Master连接超时时间(单位是秒)
 # deprecated, to be removed in MooseFS 1.7
 # LOCK_FILE = /var/run/mfs/mfsmetalogger.lock
```

#### changelog_ml.\*.mfs文件
> changelog_ml.\*.mfs是MooseFS文件系统的元数据的changelog日志(备份的Master 的Master的changelog日志)

#### metadata.ml.mfs.back文件
> metadata.ml.mfs.back是从Master主机上下载的最新的完整metadata.mfs.back的拷贝

#### sessions.ml.mfs文件
> sessions.ml.mfs是从master下载的最新的sessions.mfs文件拷贝

### chunker服务器
> 数据真实存储的位置,实际使用中,对硬件资源消耗不是很大,最终的瓶颈在网卡和磁盘IO.

#### chunker主要配置文件

* mfschunkserver.cfg
```
 # WORKING_USER和WORKING_GROUP：是运行mfschunkserver server的用户和组；
 # SYSLOG_IDENT：是mfschunkserver server在syslog中的标识,也就是说明这是由mfschunkserver server产生的；
 # LOCK_MEMORY：是否执行mlockall()以避免mfschunkserver 进程溢出(默认为0，即否)；
 # NICE_LEVE：运行的优先级(如果可以默认是 -19; 注意: 进程必须是用root启动)；
 # DATA_PATH：metadata files and lock file存放路径,此目录下大致有以下文件：metadata，changelog，sessions，stats，lock.
 # MASTER_RECONNECTION_DELAY = 5 在失去连接之后延迟多少秒重新连接master
 # MASTER_HOST: 元数据服务器的名称或地址,可以是主机名，也可以是ip地址.只要数据存储服务器能访问到元数据服务器就行.
 # MASTER_PORT = 9420
 # MASTER_TIMEOUT = 60
 # CSSERV_LISTEN_HOST = *  #允许挂载的客户端连接的IP地址(*允许全部)
 # CSSERV_LISTEN_PORT = 9422
 # CSSERV_TIMEOUT = 5      #客户端挂载连接的超时时间(单位为秒)
 # HDD_CONF_FILENAME = /usr/local/mfs/etc/mfshdd.cfg #分配给MFS使用的磁盘空间配置文件的位置
 # HDD_TEST_FREQ = 10   # 块的测试期(单位为秒)
 # deprecated, to be removed in MooseFS 1.7
 # LOCK_FILE = /var/run/mfs/mfschunkserver.lock
 # BACK_LOGS = 50
```

#### mfshdd.cfg文件
> 目录列表（指定的）用于moosefs挂载存储

> **\*AD**:当某块磁盘发生故障后可以在前面加\*,集群便会在后续冗余中,把相应磁盘或是存储位置的数据转移到其他地方存储

### mfsclient(mount)服务器
> 客户端,安装相应挂载程序使用mfsmount -H MASTER_MFS_HOST /mnt/mfs,进行磁盘挂载.关于使用嘛,找下man吧.

* * *

## 测试
> 官网手册有详细测试信息


## 总结
> 零零散散算是把相关配置文件大致介绍一遍,没想成已经有不少内容,不多多半都是配置文件内容,感觉以上介绍离实际用处好远.准备接下来写些MFS使用相关的介绍.此篇准备随时更新.
