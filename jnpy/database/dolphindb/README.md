[多物理机集群配置官方链接](https://gitee.com/dolphindb/Tutorials_CN/blob/master/multi_machine_cluster_deployment.md#51-%E9%85%8D%E7%BD%AE%E6%8E%A7%E5%88%B6%E8%8A%82%E7%82%B9)

### 本次实验躺坑记录 v1.30.18 稳定版
- 集群只有一个controller（高可用配置例外）
- master（linux） 上跑 1个controller， 1个agent 和 1 个 datanode
- slave （win10） 跑1个agent，1个datanode

将 config 文件夹 copy 到 master 节点 server 文件夹下

> 注意改下局域网 ip

agent.cfg copy 到集群的其他机器
> **注意！只更改 localsite 的 ip**

### 启动集群
1. 按照链接中的命令行模式启动，linux先启动
```
nohup ./dolphindb -console 0 -mode agent -home data -config config/agent.cfg -logFile log/agent.log &
```

2. 启动 win10
```
dolphindb.exe -mode agent -home data -config config/agent.cfg -logFile log/agent.log
```

3. 启动linux controller
```
nohup ./dolphindb -console 0 -mode controller -home data -config config/controller.cfg -clusterConfig config/cluster.cfg -logFile log/controller.log -nodesFile config/cluster.nodes &
```

4. 如果windows跑 controller，按照下面这个启动
```
dolphindb.exe -mode controller -home data -config config/controller.cfg -clusterConfig config/cluster.cfg -logFile log/controller.log -nodesFile config/cluster.nodes
```

### 集群 web 管理界面
controller ip : 8990

> 系统管理员帐号名: admin
> 
> 默认密码: 123456