# socket-py

这个项目旨在做一个帮助搭建一个较为通用的通信环境。

## 如何确定是谁发回来的包

TCP的连接？

用IP地址？

先能跑通。

### 方法1：
用一个标号

client <-> router

## client.py

msg type:

- 1: from router

## router.py

msg type:

- 1: From client
- 2: From aid
- 3: From server

## aid


## 问题

### 如果采取TCP，什么时候能关闭连接
