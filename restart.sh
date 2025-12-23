#!/bin/bash
# 修仙MUD重启脚本

echo "正在停止Evennia服务器..."
evennia stop

echo "等待服务器完全停止..."
sleep 3

echo "正在启动Evennia服务器..."
evennia start

echo "服务器启动完成！"
echo "Web客户端地址: http://localhost:4001"
echo "MUD客户端地址: localhost:4000"