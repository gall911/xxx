# 僵尸NPC管理说明

## 使用方法

### 1. 查看僵尸状态
```bash
cd /home/gg/xxx
python manage_zombie.py status
```

### 2. 设置僵尸为无敌状态
```bash
cd /home/gg/xxx
python manage_zombie.py invincible
```

### 3. 设置僵尸为可被击杀状态
```bash
cd /home/gg/xxx
python manage_zombie.py mortal
```

## 功能说明

- **无敌状态**: 当僵尸处于无敌状态时，任何攻击都不会对其造成伤害，攻击者会收到"你的攻击对僵尸无效"的提示。
- **可被击杀状态**: 当僵尸处于可被击杀状态时，它会像普通NPC一样受到伤害，HP会减少。

## 注意事项

1. 运行这些命令不需要进入Evennia shell，避免了系统无响应的问题。
2. 僵尸NPC必须已经在游戏中创建，命令才能生效。
3. 可以随时切换僵尸的无敌状态，无需重启服务器。