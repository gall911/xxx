r"""
Evennia settings file.

The available options are found in the default settings file found
here:

https://www.evennia.com/docs/latest/Setup/Settings-Default.html

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "xxx"


######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")
SILENCED_SYSTEM_CHECKS = ["models.W042"]

# 减少日志输出
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'WARNING',  # 改为WARNING减少输出
        },
    },
}

######################################################################
# 密码验证配置
######################################################################
# 清空密码验证列表，允许任意简单的密码（如 "12", "aa"）
# 同时也解除了 "密码不能与账号相似" 的限制
AUTH_PASSWORD_VALIDATORS = []
######################################################################
# 指定未登录时使用的指令集
CMDSET_UNLOGGEDIN = "commands.menu_login.UnloggedinCmdSet"
AMP_HOST = '127.0.0.1'

# 确保其他接口也是纯 IPv4
AMP_INTERFACE = '127.0.0.1'
WEBSERVER_INTERFACES = ['127.0.0.1']
ssh_INTERFACE = '127.0.0.1'
TELNET_INTERFACES = ['127.0.0.1']