# socket-py

这个项目旨在做一个帮助搭建一个较为通用的通信环境。

## 示例IP地址分配

- client：192.168.80.134
- router: 192.168.80.135
- aid:    192.168.80.136
- server: 192.168.80.137

## 各部分

### client.py

msg type:

- 1: from router

### router.py

msg type:

- 1: From client
- 2: From aid
- 3: From server

### aid


## 实现细节
### 如何确定是谁发回来的包

TCP的连接？

用IP地址？

先能跑通。

#### 方法1：
用一个标号

client <-> router: 1

router <-> aid:    2

router <-> server: 3

## 问题

### 如果采取TCP，什么时候能关闭连接

### 如何让代码更加通用

- 便于修改发送内容
- 便于修改网络拓扑
