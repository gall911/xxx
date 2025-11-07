#!/usr/bin/env python
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.conf.settings')
django.setup()

from typeclasses.rooms import Room
from evennia.utils import create

# 创建第一个修仙房间
room1 = create.create_object(
    Room,
    key="彩虹仙洞",
    location=None
)
room1.db.desc = "|y金|c光|r闪|g耀|b的|m仙|Y洞|C，|R充|G满|B灵|M气|w。"

# 创建第二个修仙房间
room2 = create.create_object(
    Room,
    key="七彩云台",
    location=None
)
room2.db.desc = "|R赤|Y橙|G黄|B绿|C青|M蓝|P紫|w云|y端|c修|r炼|g台|b。"

# 将两个房间连接起来
room1.db.exits = {
    "east": {
        "destination": room2,
        "desc": "通往七彩云台。"
    }
}
room2.db.exits = {
    "west": {
        "destination": room1,
        "desc": "返回彩虹仙洞。"
    }
}

print("已成功创建两个修仙房间：彩虹仙洞和七彩云台")
