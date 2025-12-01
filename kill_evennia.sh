#!/bin/bash
pkill -9 -f "twistd.*evennia"
pkill -9 -f "evennia.*server"
rm -f server/server.pid server/portal.pid
echo "Evennia 已强制关闭"
