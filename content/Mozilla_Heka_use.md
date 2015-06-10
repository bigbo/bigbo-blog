Title: Mozilla Heka使用
Date: 2015-05-23 10:40
Modified: 2015-05-27 23:30
Category: Technology
Tags: 文件监听,日志处理,日志转发
Slug: mozilla_heka
Author: ljingb

监控中时常需要对重要日志进行实时收集分析,之前一直使用 `logstash` 來做agent,由于 `logstash` 对系统强依赖 `Java_JDK` ,从而使用起来需要受系统环境限制.
作为对日志转发工具,对系统环境有限制的情况下可以有两个选择:

 1. [awesant](https://github.com/bloonix/awesant) :基于perl写的轻量级logstash
 2. [heka](https://github.com/mozilla-services/heka) :后面重点介绍


----------

## 0x01 Heka简介
Heka 是 Mozilla 公司仿造 logstash 设计,用 Golang 重写的一个开源项目.采用了类 logstash 的 input -> splitters -> decoder -> filter -> encoder -> output 的流程概念.其特点在于,在中间的 decoder/filter/encoder 部分,设计了 sandbox 概念,可以采用内嵌 lua 脚本做这一部分的工作,降低了全程使用静态 Golang 编写的难度.此外,其 filter 阶段还提供了一些监控和统计报警功能.

官网地址见：http://hekad.readthedocs.org/

----------

## 0x02 架构简述
Heka 内部对数据的过滤;转发等,都是采用指针形式.有着高并发,速度快等特点(实际测试监听文件转发至 Kafka 速度是 logstash 的10倍左右) ,目前 heka 可以支持多种格式的消息.
对日志处理流程如下:

` [input] -> [splitter] -> [decoder] -> [filter] -> [encoder] -> [output] `

 - [input]:
输入插件从外部获得数据,并将其读入Heka管道进行处理,支持数据读取方式包含:网络传输(tcp/udp),消息队列支持(AMQP/KAFKA),文件监听等多种方式.
 - [splitter]:
 对数据流进行分流,以区分不同来源日志.
 - [decoder]:
 对数据流进行编码,把 message 的结构各个属性解析出来,支持 Lua 对数据进行编码处理.
 - [filter]:
 Heka的处理引擎,可以对数据流进行过滤逻辑,包含统计/聚合甚至做些统计等操作.
 - [encoder]
 相对[decoder]来说是互逆操作,重新把消息内容编码为一定的格式,格式化输出.
 - [output]
 根据指定的匹配规则把某类型的消息输出到外部系统,支持多种协议和方式.

以上是整个流程各个步骤实现的功能,当然实际使用的话,这几步不是必须都要有的,如果接收到的数据,没有加密或其他特殊格式需要单独编码,可以直接处理,那Decoder就不需要. 甚至不想输出任何东西,不提供Outputs都可以.

----------

## 0x03 Heka 配置使用
Heka的配置文件要设置好所需要的 Input/Decoder/Filter/Encoder/Output(不需要的可以不配置).
以对文件进行实时监听为例:

```
#hekad的资源配置
[hekad]
#使用CPU核心数,最大性能是设置为CPU核心数*2,需要合理配置
maxprocs = 24
#heka的PID记录文件,便于监控heka进程的死活
pid_file = '/var/log/heka.pid'

#数据处理类,根据实际情况自己命名,eg:heka_test
[heka_test]
#input使用类型,根据实际情况选择
type = "LogstreamerInput"
#记录当前文件的读取位置保存目录,会把当前读取文件位置写入文件(文件名默认为:数据流的命名,例如这里为heka_test)
journal_directory = "/tmp/heka"
#被监听文件目录
log_directory = "/data0/nginxlogs"
#正则匹配路径此处是匹配log_directory后面的路径,例如现在监听的文件路径为
#/data0/nginxlogs/2015/05/23/test.log
file_match = '(?P<Year>\d+)/(?P<Month>\d+)/(?P<Day>\d+)/(?P<FileName>[^/]+)\.log'
#排序,以match匹配到的年月日对文件进行排序依次监听读取
priority = ["Year","Month","Day"]
#日志的最后修改时间在oldest_duration时间后,则不会监听
#heka 0.9.1及以前版本此处有bug,该设置无效
oldest_duration = "1h"
#分类设置,内部是修改全局变量 Logger,以备后面对日志流做来源区分,默认则为数据处理类名
differentiator = ["FileName","-","test"]

#编码设置
[PayloadEncoder]
#在每行log后面不自动添加"\n"
append_newlines = false

#output设置,同input设置
[test]
#output到kafka
type = "KafkaOutput"
#过滤log的类型,对不同日志发送到不同位置,"Logger == 'a-test'其中a-test指数据流名即全局变量 Logger 的值
message_matcher = "Logger == 'a-test'"
#写入哪个topic,或是采用 topic_variable 自动写入相应数据流对应topic
topic = "test"
#kafka机器列表
addrs = ["192.1.19.1:9092","192.1.19.2:9092"]
#采用相应编码输出
encoder = "PayloadEncoder"
```

配置文件写好规则后可以使用 `heka-logstreamer` 来查看匹配规则的是否是想要监听的文件.如下命令: 

```
$ heka-logstreamer -config=test.toml
```
没问题的话,就可以愉快的把玩heka了.

```
hekad -config=test.toml
```

----------

## 0x04 简单调试
整个来看配置文件的编写上手不是太简单,使用过程中有些规则的使用需要不断的调试.每次使用时可以通过先把log打印到终端进行简单调试来对规则进一步优化调整.
日志直接输出到终端配置如下:
```
#相同地方不做注释,同上
[hekad]
maxprocs = 24
pid_file = '/var/log/heka.pid'

[heka_test]
type = "LogstreamerInput"
journal_directory = "/tmp/heka"
log_directory = "/data0/nginxlogs"
file_match = '(?P<Year>\d+)/(?P<Month>\d+)/(?P<Day>\d+)/(?P<FileName>[^/]+)\.log'
priority = ["Year","Month","Day"]
oldest_duration = "1h"
differentiator = ["FileName","-","test"]

#编码设置
[RstEncoder]

#输出每条日志的所有结构内容
[LogOutput]
message_matcher = "TRUE"
encoder = "RstEncoder"

```

以上配置文件可以输出每条日志的所有结构信息值,包含系统的全局变量,显示例如:
```
:Timestamp: 2015-05-20 09:34:19.386066825 +0000 UTC
:Type: logfile
:Hostname: xxx
:Pid: 0
:Uuid: aad4ca95-0332-4cf6-af06-ae7729788d29
:Logger: a-test
:Payload: <message>
```
在输出之前可以通过此方法进行调试判断.

----------

当然以上纯属测试体验简介,其实heka功能还是很强大的,支持多种协议和消息队列,更多的数据流处理可以在后续去体验挖掘.