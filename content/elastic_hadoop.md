Title: elasticsearch之hadoop插件使用
Date: 2015-02-28 18:40
Modified: 2015-03-19 23:30
Category: Technology
Tags: elasticsearch 快照,elasticsearch plugin,HDFS
Slug: elasticsearch_hadoop
Author: ljingb

## elastic与Hadoop的连接

几个月前,由于资源有限,而需求无限,不得已想到es与hadoop的连接,本来想的很好,尝试把HDFS作为es的存储后端,把index存入HDFS中,这样就能节省存储空间了.当然官网也有相关使用配置(这里就不介绍了),经过几天的奋斗还是没能实现当初的想法,也幸亏没实现,实现了性能也是一大坑(猜测性能非常差以至于官方的 [elasticsearch-hdfs](https://github.com/elastic/elasticsearch-hdfs) 插件都几年没更新了!).

不过倒是尝试了把HDFS作为后端存储,可以实现备份elasticsearch数据快照到HDFS或者是从HDFS中恢复数据.选择插件 [repository-hdfs](https://github.com/elastic/elasticsearch-hadoop/tree/master/repository-hdfs),其实就是使用了ES的 `snapshot/restore` 功能.

## 安装插件

我的es版本为 `1.3.9-1`,注意: `1.3.0-1.3.7 and 1.4.0-1.4.2` 存在[Grooy漏洞](https://www.elastic.co/blog/elasticsearch-1-4-3-and-1-3-8-released/),所以选择版本的时候注意下,插件选择版本对应为2.0.2,后端Hadoop为2.5.0,安装方式如下: 

```
./bin/plugin -i elasticsearch/elasticsearch-repository-hdfs/2.0.2
```

当然像我这样没外网的可以选择 [插件下载](https://oss.sonatype.org/content/repositories/snapshots/org/elasticsearch/elasticsearch-repository-hdfs/),选择对应的版本,解压拷贝到es的plugin目录.

## 配置使用

#### 直接用curl法:

```
curl -XPUT 'http://localhost:9200/_snapshot/backup' -d '{
  "type": "hdfs",
    "settings": {
            "uri": "hdfs://hadoop:8020",
            "path": "/test/es",
            "conf_location": "hdfs-site.xml"
    }
}'
```

返回 `{"acknowledged":true}` 表示创建成功.

##### 查看创建的配置:

```
curl http://localhost:9200/_snapshot/_all
```

可以看到返回刚才配置信息.

##### 测试备份数据

```
curl -XPUT "localhost:9200/_snapshot/backup/snapshot_1?wait_for_completion=true"
```

尝试去看下HDFS上是否有刚才备份的文件,访问 `http://hadoop:50070/explorer.html#/test/es` 便可以看到相关的快照文件.

##### 测试还原数据

通过快照还原数据,测试前可以把之前测试做过备份的索引进行删除,然后通过如下命令进行数据恢复:

```
curl -XPOST "localhost:9200/_snapshot/backup/snapshot_1/_restore?wait_for_completion=true"
```

#### 通过kopf插件进行设置

[elasticsearch-kopf](https://github.com/lmenezes/elasticsearch-kopf),是一个对es集群管理综合插件,无需安装[体验地址](http://lmenezes.com/elasticsearch-kopf/?location=http://localhost:9200).

备份恢复快照设置如图:

![rsyslog](/pictures/es_hdfs.png u"kopf设置")


