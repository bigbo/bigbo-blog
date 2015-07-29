Title: 引发Elasticsearch OOM之type
Date: 2015-07-20 13:40
Modified: 2015-07-28 21:00
Category: Technology
Tags: elasticsearch oom, elasticsearch 调优
Slug: elasticsearch_oom
Author: ljingb

开源日志处理哪家强?当数 [ELKstack](https://www.elastic.co/) ,但搭起来容易用起来难,尤其是ES,小脾气那叫一个多,不好好调教下时不时的就会给你来点颜色,什么脑裂,内存不足 `OOM`,要不就是索引过慢,性能跟不上;应有尽有,自从用起来,一把心酸.

最近又出问题了,之前好好的集群(已经正常运行3个多月了),当新接入了一个服务(大部分只有写),变得频繁罢工,一周就要重启4次左右,搞得身心疲惫,终于发现故障的原因,故记之,警示后人.

* * *

## 0x01 ES 几个基本概念

###  集群

* cluster (集群)
代表一个集群,集群中有多个节点,其中有一个为主节点,这个主节点是可以通过选举产生的(可以设定主节点角色),主从节点是对于集群内部来说的.es的一个概念就是去中心化,字面上理解就是无中心节点,这是对于集群外部来说的,因为从外部来看es集群,在逻辑上是个整体,你与任何一个节点的通信和与整个es集群通信是等价的.

* shards (分片)
代表索引分片,es可以把一个完整的索引分成多个分片,这样的好处是可以把一个大的索引拆分成多个,分布到不同的节点上.构成分布式搜索.分片的数量只能在索引创建前指定,并且索引创建后不能更改.

* replicas (副本)
每个主分片可以有零个或多个副本.副本是主分片的一个拷贝,有两个作用:

 1. 故障转移:如果主分片有问题,副本分片可以提升为主分片;
 2. 提高性能:获取和搜索请求可以处理主分片或副本分片.当然,注意副本不是越多越好!

 默认情况下,每个主分片有一个副本,不过索引的副本数量可以动态地改变.在同一个节点上,一个副本分片将永远不会和其主分片一起运行.

### 文档元数据
* index (索引)
索引就是像关系数据库中的"数据库".通过映射可以定义成多种类型.
索引是一个逻辑命名空间映射到一个或多个主要的分片,可以有零个或多个副本分片.

* document (文档)
文档是存储在elasticsearch中的一个JSON文件.这是相当与关系数据库中表的一行数据.每个文档被存储在索引中,并具有一个类型和一个id.一个文档是一个JSON对象(也被称为在其他语言中的 hash / hashmap / associative array(关联数组)),其中包含零个或多个字段 或者键值对.

 原始JSON文档将被存储在索引的_source字段.在获得(getting) 或者搜索(searching)默认的返回时,得到或搜索文档.

* mapping (映射):
映射是像关系数据库中的"模式定义".每个索引都有一个映射.它定义了每个索引的类型.再加上一些索引范围的设置.映射可以被明确地定义,或者在一个文档被索引的时候自动生成.

* type (类型):
Type是相当于关系数据库中的"表".每种类型都有一列字段,用来定义文档的类型.映射定义了对在文档中的每个字段如何进行分析.

* source field (源字段)
默认情况下,你的JSON文档将被索引存储在_source字段里面,所有的get(获取)和search(搜索)请求将返回的该字段。这将允许你直接从搜索结果中访问到源数据，而不需要再次发起请求检索。
注：索引将返回完整的的JSON字符串给你，即使它包含无效的JSON。此字段里的内容不表示任何该对象里面的数据如何被索引。

* field (字段)
文档中包含的一组字段或键值对.字段的值可以是一个简单的(标量)值(如字符串,整数,日期),或者一个嵌套的结构就像一个数组或对象.一个字段就是类似关系数据库表中的一列.

 映射的每个字段有一个字段的类型"type" ( **不要与文档类型混淆** ),表示那种类型的数据可以存储在该字段里,如:整数 `<integer>` , 字符串 `<string>` , 对象 `<object>` .映射还允许你定义(除其他事项外)一个字段的值如何进行分析.

* id (标识)
每个文档ID标识了一个文档.一个文档的 索引/类型/ ID 必须是唯一的.如果没有提供ID,将是自动生成. (还可以看到路由 `<routing>` ）

### 角色关系对照

elasticsearch 跟 MySQL 中定义数据格式的角色关系对照表如下:

| MySQL    |  备注 | elasticsearch | 备注 |
| -------- | ------ | ------- | -------- |
| database |many tables |index | many types|
| table    |many rows;one schema |type | many documents;one mapping|
| row      | many columns |document | many fields|


以上都是一些基本概念的解释,参照对比MySQL,可以大致了了解ES存储结构关系.

***

## 0x02 故障回顾

### 问题发生现象
前天新接入一个需求,在elasticsearch建立索引,总是在不久之后崩溃,查看日志,ES甩出一坨坨内存不够用的警告,日志中并伴随着有java OutOfMemoryError的错误信息.用如下命令查看索引状态,发现在建的索引健康状态为Green.

```
curl -XGET 'http://localhost:9200/_cat/health'
```

日志内存不足warn:
```
[2015-07-21 11:39:01,458][WARN ][monitor.jvm              ] [Fagin] [gc][old][83840][226] duration [15.1s], collections [1]/[16.2s], total [15.1s]/[6.3m], memory [3.4gb]->[2.7gb]/[3.8gb], all_pools {[young] [731.6mb]->[115.9mb]/[1gb]}{[survivor] [136.5mb]->[0b]/[136.5mb]}{[old] [2.5gb]->[2.6gb]/[2.6gb]}
```

然后逐渐有的节点不接受请求和响应,逐渐的脱离集群.

```
[2015-07-21 11:45:25,978][WARN ][discovery.zen.publish    ] [Fagin] timed out waiting for all nodes to process published state [28846] (timeout [30s], pending nodes: [[Silvermane][o8o6aA_fTEu7TJnKlP9zNA][110-19-179.org][inet[/192.9.19.179:9300]]])
```

### 问题追查及分析
推测是由于内存分配的太小导致,于是重启服务,把内存调整到32G内存重启跑起来,并且对JVM的GC过程添加监控,以为从此可以安心睡觉了.但是想不到悲剧即将发生.不到8个小时,内存又要被撑爆了!于是继续追查原因.

新建立一个小集群,小集群所有服务配置和大集群配置一样,唯一不同的是内存只分配为2g(大集群内存分配32G),开启双写模式,数据同时写入两个集群.

通过对日志的查看以及对jvm的监控,发现日志中有大量的WARN,而且每条都不重复
```
[WARN ][index.mapper             ] [Blue Marvel] [2015-07-21_history] Type [xz@rl_tab@/tieba/Theme_17.html] contains a '.', it is recommended not to include it within a type name
........
```
于是想起前几天接入的新的业务,可能是type字段有些非法字符,感觉不是问题所在,所以可以忽略.

在开启双写模式下,经过不到1个小时的时间,小集群内存就OOM了,集群瘫痪无相应了.此时开始注意到上面说的WARN,并根据实际数据写入量做分析,发现实际写入数据size也就不到2g左右,集群内存就被撑爆,而我的硬盘空间远远大于2g存储空间,感觉所有数据都被存到内存当中了,而不是存到硬盘当中了.于是打开监控查看之前OOM的整个历史记录.
![elasticsearch_oom1](/pictures/es_oom1.png u"es_oom")

***

## 0x03 故障分析总结
通过上面监控发现,随着我的数据写入量的增大,jvm每次完整一次gc后可用内存越来越少,存在内存泄露.而日志中继续不断报WARN.此时查看对应索引的mapping,发现长时间无法返回结果,查看数据写入逻辑得知,写入数据index中的type被当成一个变量,也就是每一个关键词都会在mapping中生成一个"[关键词]"的type,于是这会导致ES得到一条日志就会 `update_mapping` ,更新 `cluster.metadata`, `type` 是 `mapping` 中的一部分, `mapping` 也用于配置元数据和type之间的关系;以上的使用可以理解为每有一个关键字,就会新建一张表,而 `mapping` 是元数据,需要加载到内存,来管理各个索引每个对应字段的,最终会得到一个非常庞大的 `mapping` ,从而内存不足,造成集群响应不了从而假死宕机.

以上都是理论,实践出真知,在服务没有宕机之前赶紧把有问题索引干掉,于是美好的事情发生了,内存回收正常,通过上图可以看到18:30分以后的监控数据是删掉有问题索引以后的jvm gc过程,一切恢复正常.

es索引的结构 `index -> shard -> segment` ,是这样一个逻辑,如果用户搜 `/index/type/_search` , 就需要有个办法快速过滤出满足需要的数据集,type是被索引起来的.有两种使用方式注意: **不同type下不同field的类型如果不一样** 以及 **不同_type下相同field** 都会在mapping新生成一个type,还是会浪费mapping空间,所以使用上需要注意.

但凡集群不稳定经常OOM的话就需要追查原因了,首先要做到有据可查,也就是要把能加监控的加监控,观察宕机情况,然后查看log,log的记录还是很详细的,跟着log來查相应原因,一般都好解决.

***

## 0x04 其他OOM的原因及注意
默认情况ES对字段数据缓存(Field Data Cache)大小是无限制的,查询时候会把字段放到内存做缓存,特别是facet查询(kibana3),对内存要求非常高,它会把结果放到内存,然后进行排序等操作,一直使用内存,直到内存用完,当内存不够用时就有可能出现out of memory 问题.在配置的时候需要注意cache.field相关设置.

***

关于ES相关文档：
Elasticsearch权威指南1 [^ES_BOOK1]
ElasticSearch 权威指南2 [^ES_BOOK2]

[^ES_BOOK1]: https://www.gitbook.com/book/looly/elasticsearch-the-definitive-guide-cn/details

[^ES_BOOK2]: https://www.gitbook.com/book/fuxiaopang/learnelasticsearch/details
