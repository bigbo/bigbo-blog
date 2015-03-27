Title: logstash-input-file以及logstash-output-kafka插件性能测试
Date: 2015-03-26 14:40
Modified: 2015-03-27 19:30
Category: Technology
Tags: kafka,消息队列,logstash插件,日志处理
Slug: logstash_performance
Author: ljingb

最近项目需求,要了解下logstash的一些性能,根据现有的技术方案,主要是针对 `logstash-input-file` 插件以及 `logstash-output-kafka` 插件进行测试,不过最近关注 logstash 的人应该清楚,目前处于新老版本迭代期,老版本[1.4.2版本](https://download.elasticsearch.org/logstash/logstash/logstash-1.4.2.tar.gz) 和新版本 [1.5.0RC2版本](http://download.elasticsearch.org/logstash/logstash/logstash-1.5.0.rc2.tar.gz) ,[1.4.2版本内存泄露](http://chenlinux.com/2015/02/10/logstash-outputs-elasticsearch-http-memory-leak/) 问题在1.5版本后得到改进,但是1.5还没出正式版本.以下是根据1.5RC2版本来进行测试对比.

硬件环境:

|CPU|  硬盘|  内存|
|-------|-------|-------|
|Intel CorporationXeonE5 v2/Core i7 |    2TX1 |    128G |

>

软件环境:

| 系统       | java_jdk  |  JVM                          | Kafka Configuration     |
| ------------- |:------------:|:-----------------------------:|:---------------------------:|
| centos6.5  |  1.7.0_65 | -Xmx2000m -Xss2048k(其他默认) | Replica X1 Partition X1 |

* * *

## 各版本之间性能对比

### 裸跑性能

先测试下两个版本裸跑性能(不加任何filter),官方在之前也出过关于为什么用JRuby而不是用MRI的 [性能测试报告](https://gist.github.com/jordansissel/4171039),以下测试也选择官方的测试方法:使用 `generator` 插件产生数据,然后使用 `pv` 命令做性能监控.out.conf文件如下:

```
input {
 generator { count => 5000000 }
}

output {
    stdout {
        codec => dots
    }
}

```

```
$ ./bin/logstash agent -f out.conf | pv -Wbart > /dev/null
```

* 注意:centos下yum安装的 `pv` 版本相对较低,没有 `-a` 这个参数,使用起来不太好观察,可以选择更新下 [新版本](http://pkgs.repoforge.org/pv/).

logstash1.4.2裸跑性能:

```
1.53MiB 0:00:34 [47.2kiB/s] [46.2kiB/s]
1.97MiB 0:00:44 [37.9kiB/s] [45.9kiB/s]
2.81MiB 0:01:03 [38.3kiB/s] [45.7kiB/s]
```

logstash1.5.0RC2裸跑性能:

```
1.41MiB 0:00:52 [25.6kiB/s] [27.8kiB/s]
1.65MiB 0:01:00 [  26kiB/s] [28.1kiB/s]
2.19MiB 0:01:19 [  31kiB/s] [28.4kiB/s]
```

裸跑性能见分晓了.不解的是不知道为什么1.5RC2的版本与1.4.2版本的差距那么大.好奇心的驱使,去翻了下github的 [issues](https://github.com/elastic/logstash/issues/2870#issuecomment-86515699).看来确实新版本有些性能倒退,根据上面说的使用其修改版本 `fix/perf_regression` 测试性能如下:

```
 941kiB 0:00:26 [31.9kiB/s] [36.2kiB/s]
2.86MiB 0:01:20 [36.2kiB/s] [36.2kiB/s]
```

对比修改前1.5.0RC2版本确实有提升(其实提升性能更大的是在filter的时候).但实际测试提升没有issues中作者写的那么大.


### logstash-input-file性能对比

有了上面的结果现在对后续结果也有些预估,下面的测试只需把上面的配置文件稍作修改,修改成监听文件模式:

```
input {
    file {
        path => "/data0/lijingbo/0.log"
     }
}

output {
    stdout {
             codec => dots
    }
}

```

命令同上:

```
$ ./bin/logstash agent -f out.conf | pv -Wbart > /dev/null
```

logstash1.4.2性能:

```
2.31MiB 0:01:18 [34.9kiB/s] [30.3kiB/s]
2.39MiB 0:01:21 [27.3kiB/s] [30.3kiB/s]
2.48MiB 0:01:24 [34.7kiB/s] [30.3kiB/s]
2.65MiB 0:01:29 [42.3kiB/s] [30.5kiB/s]
2.81MiB 0:01:34 [  36kiB/s] [30.6kiB/s]

```

logstash1.5.0RC2性能:

```
 376kiB 0:00:20 [23.9kiB/s] [18.8kiB/s]
 498kiB 0:00:25 [27.1kiB/s] [19.9kiB/s]
 777kiB 0:00:39 [22.4kiB/s] [19.9kiB/s]
 2.08MiB 0:01:44 [20.1kiB/s] [20.4kiB/s]
```

logstash1.5.0fix版本性能:

```
 673kiB 0:00:27 [  31kiB/s] [24.9kiB/s]
 896kiB 0:00:36 [26.5kiB/s] [24.9kiB/s]
1.09MiB 0:00:45 [25.3kiB/s] [24.8kiB/s]
1.86MiB 0:01:17 [19.1kiB/s] [24.7kiB/s]
1.91MiB 0:01:19 [29.7kiB/s] [24.8kiB/s]
```

通过上面的结果,高下立判了.对于文件读取直接输出转发的话还是1.4.2性能比较好.

* * *

### logstash-output-kafka性能对比

对于kafka的输出,由于 `1.4.2版本` 当时没有把kafka的插件并入到logstash的默认设置里.所以在此选择手工安装 [此前介绍过](http://bigbo.github.io/pages/2015/01/23/logstash_kafka/),所选各个插件版本如下:

* logstash1.4.2 + kafka_2.10-0.8.1.1 + logstash-kafka-0.6.2 + jruby-kafka-0.2.1-java

* logstash 1.5.0RC2 + logstash-output-kafka 0.1.8

* [logstash 1.5.0 (fix/perf_regression branch)](https://github.com/elastic/logstash/tree/fix/perf_regression) + logstash-output-kafka 0.1.8

对此其实可以根据github上的issues追溯到还是之前的作者对此方面有 [相关测试](https://github.com/elastic/logstash/issues/2899)

* * *

#### 同步模式

配置文件如下:

```
input {
 generator { count => 30000000 }
}

output {
    stdout {
             codec => dots
    }
  kafka {
    broker_list => "localhost:9092"
    topic_id => "test"
    compression_codec => "snappy"
  }
}
```
以上配置其实就是默认配置,默认配置一些选项未列出,其实默认配置走的是 `sync` 模式.

执行命令:

```
$ ./bin/logstash agent -f out.conf | pv -Wbart > /dev/null
```

logstash1.4.2 + kafka_2.10-0.8.1.1 + logstash-kafka-0.6.2 + jruby-kafka-0.2.1-java 性能:

```
 191kiB 0:01:04 [3.54kiB/s] [   3kiB/s]
 233kiB 0:01:17 [2.92kiB/s] [3.04kiB/s]
 275kiB 0:01:29 [3.71kiB/s] [ 3.1kiB/s]
 329kiB 0:01:45 [3.08kiB/s] [3.14kiB/s]
```

logstash 1.5.0RC2 + logstash-output-kafka 0.1.8 性能:

```
 456kiB 0:01:32 [5.41kiB/s] [4.96kiB/s]
 505kiB 0:01:41 [5.88kiB/s] [   5kiB/s]
 557kiB 0:01:51 [4.85kiB/s] [5.02kiB/s]
 598kiB 0:01:59 [5.69kiB/s] [5.03kiB/s]
```

logstash 1.5.0 (fix/perf_regression branch) + logstash-output-kafka 0.1.8 性能:

```
 440kiB 0:01:15 [7.09kiB/s] [5.88kiB/s]
 569kiB 0:01:34 [7.03kiB/s] [6.05kiB/s]
 616kiB 0:01:41 [7.21kiB/s] [ 6.1kiB/s]
 630kiB 0:01:43 [7.44kiB/s] [6.12kiB/s]
```

* * *

#### 异步模式

配置文件如下:

```
input {
 generator { count => 30000000 }
}

output {
    stdout {
             codec => dots
    }

  kafka {
    topic_id => "test"
    compression_codec => "snappy"
    request_required_acks => 1
    serializer_class => "kafka.serializer.StringEncoder"
    request_timeout_ms => 10000
    producer_type => 'async'
    message_send_max_retries => 5
    retry_backoff_ms => 100
    queue_buffering_max_ms => 5000
    queue_buffering_max_messages => 10000
    queue_enqueue_timeout_ms => -1
    batch_num_messages => 1000
  }
}

```

此配置其实同issues上的配置相同,主要是我上面测试出来的跟已有的结果差距甚大,顾选择此配置再次测试.

logstash1.4.2 + kafka_2.10-0.8.1.1 + logstash-kafka-0.6.2 + jruby-kafka-0.2.1-java 性能:

```
 796kiB 0:01:07 [12.6kiB/s] [11.9kiB/s]
 834kiB 0:01:10 [  12kiB/s] [11.9kiB/s]
 967kiB 0:01:20 [13.7kiB/s] [12.1kiB/s]
1.08MiB 0:01:31 [12.5kiB/s] [12.1kiB/s]
1.11MiB 0:01:33 [15.7kiB/s] [12.2kiB/s]
```

logstash 1.5.0RC2 + logstash-output-kafka 0.1.8 性能:

```
 649kiB 0:01:14 [7.79kiB/s] [8.77kiB/s]
 711kiB 0:01:20 [11.6kiB/s] [8.89kiB/s]
 769kiB 0:01:26 [10.4kiB/s] [8.95kiB/s]
 901kiB 0:01:39 [9.31kiB/s] [ 9.1kiB/s]
```

logstash 1.5.0 (fix/perf_regression branch) + logstash-output-kafka 0.1.8 性能:

```
 712kiB 0:01:16 [9.66kiB/s] [9.38kiB/s]
 765kiB 0:01:21 [11.4kiB/s] [9.45kiB/s]
 843kiB 0:01:29 [10.5kiB/s] [9.48kiB/s]
 884kiB 0:01:33 [  11kiB/s] [9.51kiB/s]
 945kiB 0:01:39 [9.38kiB/s] [9.55kiB/s]

```

结果显而易见了.不知道1.5版本性能问题会不会到正式解决或是提高.到时再来测试一翻.

### logstash-input-file + logstash-out-kafka 性能对比

既然单独的插件测试过了, 综合的测试下两个一起使用的效果.所有条件均同上,差别仅是配置文件(异步模式).

```
input {
  file {
    path => "/data0/lijingbo/0.log"
  }
}

output {
  stdout {
    codec => dots
  }
  kafka {
    topic_id => "test"
    compression_codec => "snappy"
    request_required_acks => 1
    serializer_class => "kafka.serializer.StringEncoder"
    request_timeout_ms => 10000
    producer_type => 'async'
    message_send_max_retries => 5
    retry_backoff_ms => 100
    queue_buffering_max_ms => 5000
    queue_buffering_max_messages => 10000
    queue_enqueue_timeout_ms => -1
    batch_num_messages => 1000
  }
}
```

命令执行同之前.

logstash1.4.2性能:

```
 735kiB 0:01:28 [12.9kiB/s] [8.36kiB/s]
 832kiB 0:01:36 [10.2kiB/s] [8.67kiB/s]
 898kiB 0:01:41 [14.1kiB/s] [ 8.9kiB/s]
 946kiB 0:01:45 [13.6kiB/s] [9.01kiB/s]
```

logstash1.5RC2性能:

```
 720kiB 0:01:21 [11.6kiB/s] [8.89kiB/s]
 792kiB 0:01:29 [8.74kiB/s] [8.91kiB/s]
 851kiB 0:01:35 [10.1kiB/s] [8.96kiB/s]
 891kiB 0:01:39 [9.92kiB/s] [   9kiB/s]

```

logstash1.5fix性能:

```
 986kiB 0:01:42 [10.8kiB/s] [9.67kiB/s]
 998kiB 0:01:43 [12.4kiB/s] [ 9.7kiB/s]
1.04MiB 0:01:50 [10.7kiB/s] [9.69kiB/s]
1.12MiB 0:01:58 [11.3kiB/s] [9.69kiB/s]
```

测试后感觉与想象中有些差距,对1.5正式版性能稳定性提升抱有希望.后续会跟进,做一些其他更多相关测试.
