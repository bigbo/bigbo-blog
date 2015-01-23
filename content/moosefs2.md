Title: MooseFS浅析(二)
Date: 2015-01-08 19:20
Modified: 2015-01-09 16:00
Category: Technology 
Tags: 分布式文件系统,Moosefs,分布式存储
Slug: Moosefs_two
Author: ljingb

##前言
继上篇,感觉说了好多废话,多半是配置文件相关参数,作为一个基础运维人员,更关注的是怎么让服务更加稳定(高可用),出现问题如何恢复(容错)等,更接地气的东西打算在下面介绍下.

* * *

##启动和关闭顺序

> master启动后,metalogger\chunker\client三个元素都能自动与master建立连接.

> > 正常启动顺序:matser---chunker---metalogger---client.

> > 关闭顺序:client---chunker---metalogger---master

* * *

##client操作影响
> 客户端强制**kill -9**杀掉**mfsmount**进程,需要先**umount**,然后再**mount**,否则会提示:

```
fuse: bad mount point `/mnt/test/': Transport endpoint is not connected
see: /data/jingbo.li/mfs/bin/mfsmount -h for help
```

* * *

##chunker的空间

> 查看MooseFS文件的使用情况,请使用**mfsdirinfo**命令,相当于**df**.

* * *

##快照**snapshot**
> 可以快照任何一个文件或目录,语法:**mfsmakesnapshot src dst**,但是src和dst必须都属于mfs体系,即不能mfs体系中的文件快照到其他文件系统.

* * *

#**mfsappendchunks**
> 追加chunks到一个文件,追加文件块到另一个文件.如果目标文件不存在,则会创建一个空文件,然后继续将块进行追加.

* * *

##回收站机制
其实MFS有类似windows的回收站这种机制,当文件不小心删除了,不用担心,去回收站去找.随时可以恢复.当然,我所说的随时随地恢复要看你回收站的数据保存多长时间了(默认24小时).

* 首先挂载辅助系统
> 单独安装或挂载**MFSMETA**文件系统,它包含目录/trash (包含仍然可以被还原的删除文件的信息)和**/trash/undel**(用于获取文件),用一个-m或-o mfsmeta的选项,这样可以挂接一个辅助的文件系统MFSMETA,这么做的目的是对于意外的从MooseFS卷上删除文件或者是为了释放磁盘空间而移动的文件而又此文件又过去了垃圾文件存放期的恢复
> > 例如:

        mfsmount -m /mnt/mfsmeta -H mfs1.com.org
        或者
        mfsmount -o mfsmeta -H mfs1.com.org /mnt/mfsmeta
> 需要注意的是,如果要挂载mfsmeta,一定要在mfsmaster的mfsexports.cfg文件中加入如下条目:* . rw
>
> 挂载后在/mnt/mfsmeta目录下分reserved和trash两个目录,trash为已删除文件存放目录,删除时间根据mfsgettrashtime设置时间来自动删除.

* 设置文件或目录的删除时间
> 一个删除的文件能够存放在“ 垃圾箱”中的时间称为隔离时间,这个时间可以用**mfsgettrashtime**命令来查看:
> > ![mfsgettrashtime命令](/pictures/mfs_pic4.png)
> > 
> > 用**mfssettrashtime**命令来设置上面的这个有效时间,要注意的是,保存时间单位为秒.
> > ![mfssettrashtime命令](/pictures/mfs_pic5.png)

* 恢复删除的文件
> 把删除的文件移到/trash/undel下,就可以恢复此文件.在MFSMETA的目录里,除了**trash**和**trash/undel**两个目录,还有第三个目录**reserved**,该目录内有已经删除的文件,但却被其他用户一直打开着.
在用户关闭了这些被打开的文件后,**reserved**目录中的文件将被删除,文件的数据也将被立即删除.此目录不能进行操作.

* * *

##单点故障解决
###官方提供解决方案

> ####从备份中恢复一个master(1.6及以上版本)
> 1. 安装一个mfsmaster
> 2. 利用同样的配置来配置这台mfsmaster(copy一份mfsmaster.cfg到备机)
> 3. 找回metadata.mfs.back文件,可以从备份中找,也可以中metalogger主机中找(如果启动了metalogger服务),然后把metadata.mfs.back放入data目录,一般为${prefix}/var/mfs.
> 4. 从在master宕掉之前的任何运行metalogger服务的服务器上拷贝最后metadata文件,然后放入mfsmaster的数据目录
> 5. 利用mfsmetarestore命令合并元数据changelogs,可以用自动恢复模式mfsmetarestore –a,也可以利用非自动化恢复模式,语法如下:mfsmetarestore -m metadata.mfs.back -o metadata.mfs changelog_ml.*.mfs

> ####DNS主从
> * 详细的就需要看官网的手册了,不过CE版本不支持,需要用PRO版本才支持.具体好不好用我也不知道.

> ####UCARP方案
> * 两台主机安装ucarp,ucarp允许多个主机共享一个虚拟的ip地址,以提供自动的故障恢复功能,当其中某个主机宕机时,其它的主机会自动接管服务,ARP协议的特点在于其非常低的开销,主机间使用加密数据传递信息,并且在冗余主机之间不需要任何额外的网络链接.

> 1. 双机采用虚拟共用一个虚拟IP地址来实现故障自动迁移,执行指令
``
    ucarp -zB -i eth1 -s 192.168.1.100 -v 42 -p moose -a 192.168.1.252 --upscript=/data/jingbo.li/mfs/sbin/vip-up --downscript=/data/jingbo.li/mfs/sbin/vip-down
``
> 当master宕机后从机可以即时启动恢复接管master的相应服务.
>
> **\***此中方案中要保证两台机器之前的网络畅通,网络抖动都可能影响服务.另外关于脚本的编写恢复策略也影响着恢复状况.我的github上有提供相关脚本.

> ####其他HA方案
> * 其他高可用方案,例如:**DRBD+Heartbeat+Pacemaker**等,更多的就请教Google吧.

 总结:
> 根据实际测试(采用ucarp方案),在有些情况下无效,当在你刚写完文件时,在断掉master后,在metalogger机器上做恢复后,客户端上不能对某些文件正常访问,会长时间地卡在那里.通过**mfsfileinfo**在查看文件属性时,会发现一些的块无效提示,在文件文件里也能看到一些提示信息.数据会丢失,完整性得不到保障.出现数据丢失或是读写错误可以尝试使用**mfsfilerepair**修复.

* * *

##补充及总结
算是对MFS实际应用做的一些总结,对于实际来说,使用情况会复杂的多,实际应用肯定会遇到好多的问题.后续根据使用情况再做些总结和规整.

另外做些补充:
> 二次开发:[百度对Moosefs二次开发](https://github.com/ops-baidu/shadow-mfs),[相关文章](http://www.zhangxiaolong.org/archives/242.html)
>
> 使用:实际使用来看,不可能使用每个客户端使用的时候都去安装其客户端,造成使用不太方便,其实可以找一台机器挂载MFS后,在其上面搭建一个**FTP**等相关文件下载或是上传的服务,再加些权限限制,这样对使用者来说就非常方便和友好了.

单线程是硬伤
> Moosefs更新其实还算快的,通过看其1.6.X版本源码,其实有些地方写的并不是很好,比如网络方面用的是**poll**,不知道为什么没有采用更高效的**epoll**,当然现在的最新版本是2.x版本,后续会跟进的.(经过查看最新版2.0.43版本,网络方面与1.6.X差别不大)
> 
> 另外,Master的单线程机制也不能够发挥多核CPU的优势,导致其性能受限,当海量文件(千万以上级别)存储的选型的时候就要注意了,也不适合高并发的一些业务.
