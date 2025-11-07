#!/usr/bin/env python
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.conf.settings')
django.setup()

from typeclasses.accounts import Account
from django.contrib.auth.hashers import make_password

# 获取超级用户账号
try:
    account = Account.objects.get(username__iexact="x")
    # 设置新密码为 "xx"
    account.password = make_password("xx")
    account.save()
    print(f"已成功重置用户 {account.username} 的密码")
except Account.DoesNotExist:
    print("找不到用户名为 'x' 的账号")
except Exception as e:
    print(f"发生错误: {e}")
