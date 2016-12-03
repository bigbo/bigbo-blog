Title: elasticsearch 服务的监控与报警
Date: 2016-10-20 18:40
Modified: 2016-11-16 16:30
Category: Technology
Tags: elasticsearch 监控&报警
Slug: elasticsearch_monitor
Author: ljingb

近段时间,由于公司报警系统结构调整,由小米开源的 [Open-Falcon](http://open-falcon.org/) 替换了原有的 Zabbix 监控系统,使得一些原自定义监控不可用,于是便着手在新监控系统下完善了 Elasticsearch 服务的监控.

## 0x01 Elasticsearch 服务架构

只谈监控不谈架构那如同耍流氓,监控可以追溯历史,查故障原因,分析瓶颈点,作为服务来说需要全面监控.

![es_monitor](/pictures/es_monitor.png u"es监控")

**注:** 
1.elasticsearch 我们是按角色部署,前面顶了个nginx,可以控制相关访问以及负载.

2.整个服务监控指的是系统的各个组件,图中有直接关联基础监控部分,也有没有关联的基础监控

***

## 0x02 可监控项

### 0x02.1 基础监控
基础监控是监控系统的基本功能,包含:CPU/IO/网络/内存等等,在此就不说了.

### 0x02.2 Nginx 日志监控
监控到用户的访问量,一些非法请求或是不正常请求情况.

### 0x02.3 Elasticsearch 日志监控
1.Elasticsearch 慢查询日志监控(需要开启慢查询日志记录)

2.服务本身日志监控,产生ERROR等异常时监控

### 0x02.4 Elasticsearch 服务指标监控
Elasticsearch 本身提供了非常完善的,由浅及深的各种性能数据接口.和数据读写检索接口一样,采用 RESTful 风格.我们可以直接使用 curl 来获取数据,编写监控程序,也可以使用一些现成的监控方案.通常这些方案也是通过接口读取数据,解析 JSON,渲染界面。

例如我之前使用的是Zabbix现成的监控也是通过restful api来获取的数据: https://github.com/Wprosdocimo/Elasticsearch-zabbix

Elasticsearch 细分为集群/节点/index级别的三个层次监控.

1.集群级别的监控

命令示例:
```
# curl -XGET 127.0.0.1:9200/_cluster/health?pretty
{
  "cluster_name" : "es1003",
  "status" : "green",
  "timed_out" : false,
  "number_of_nodes" : 38,
  "number_of_data_nodes" : 27,
  "active_primary_shards" : 1332,
  "active_shards" : 2381,
  "relocating_shards" : 0,
  "initializing_shards" : 0,
  "unassigned_shards" : 0,
  "number_of_pending_tasks" : 0
  "delayed_unassigned_shards" : 0,
  "number_of_in_flight_fetch" : 0,
  "task_max_waiting_in_queue_millis" : 0,
  "active_shards_percent_as_number" : 100.0
}
```
输出里最重要的就是 status 这行,status 有三个可能的值:

 - green 绿灯,所有分片都正确运行,集群非常健康.
 - yellow 黄灯,所有主分片都正确运行,但是有副本分片缺失.
 - red 红灯,有主分片缺失。这部分数据完全不可用.
 
所以报警规则应该设置为非绿则报警.

2.Node 级别监控

通过如下命令获取节点状态:
```
# curl -XGET 127.0.0.1:9200/_nodes/stats
```

![es_nodes_monitor](/pictures/es_nodes_monitor.png u"es_nodes监控")

返回数据的第一部分是节点概要,主要就是节点的主机名,网卡地址和监听端口等.这部分内容基础监控都可以做了，一般没有太大用途.只需要关注红框内的参数.

 - indices:这部分内容会列出该节点上存储的所有索引数据的状态统计.
> `docs.count` : 节点上存储的数据条目总数
> `store.size_in_bytes` 节点上存储的数据占用磁盘的实际大小
> `store.throttle_time_in_millis` : ES 进程在做 segment merge 时出现磁盘限速的时长.如果你在 ES 的日志里经常会看到限速声明,那么这里的数值也会偏大
> `indexing`: 显示了被索引的docs数量,是一个累计递增值,只要内部进行index操作就会增加,所以index、create、update都会增加.可以利用这个累计值,监控每分钟的变化,从而做出预警
> `get`: 显示的是调用 GET	HEAD 方法的次数,也是累计值
> `search`: 描述search 相关监控数据, `query_time_in_millis/query_total` 可以用来粗略估计搜索引擎的查询效率.

 - jvm:即 JVM 信息,主要在于 GC 相关数据.
 - thread_pool: ES 内部是保持着几个线程池,不同的工作由不同的线程池负责.一般来说,每个池子的工作线程数跟你的 CPU 核数一样.监控此项数据目的不是用作 ES 配置调优,而是作为性能监控,方便优化你的读写请求.
> `rejected`: 每个线程池格式基本一致,需要监控的是每个线程池的rejected.如果线程池队列满了,新的请求将被rejected掉,显示在rejected,这时系统负载过高或是到了瓶颈了

 - breakers:包括 request/fielddata 和 parent
> `fielddata`: 如果fielddata的大小比分配内存还大,那就会导致OOM, Elasticsearch 引入了断路器,用于预先估算内存够不够,如果不够,断路器就会被触发(tripped)并返回异常,而不至于导致OOM.所以需要监控 tripped,如果这个值很大或者说一直在增长,那么就说明查询需要优化或者说需要更多内存

3.Index 级别监控

索引状态监控接口的输出信息和节点状态监控接口非常类似,一般情况下,这个接口单独监控起来的意义并不大.
通过如下命令获取节点状态:
```
# curl -XGET 127.0.0.1:9200/index_name/stats
```

4.ES集群 服务级别监控

对于集群来说我们的关注指标往往是集群整体的性能,例如集群的整体写入性能,查询效率,并发能力等,这些指标可以直接通过每台Node节点指标叠加获取到.

***

## 0x03 总结
对于Elasticsearch来说,搭建起来用很容易,但是想用好,并调整到最优状态并不是一时可以搞定的,所以需要监控各项指标,从各个点综合考虑调优.

结合以上的分析,编写出基于Open-Falcon监控下的ES服务监控: https://github.com/bigbo/Elasticsearch-Falcon ,目前只是完成基础监控,还有待完善其他监控指标.使用有问题希望给我发issues.

相关参考连接:
* http://kibana.logstash.es/
