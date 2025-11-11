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

# Use Evennia's menu-based login (EvMenu). This makes the login flow
# ask for name and password as a series of questions handled by
# evennia.contrib.base_systems.menu_login.
#
# See documentation / contrib example. To customize the connection
# screen, point CONNECTION_SCREEN_MODULE to your own module.

CMDSET_UNLOGGEDIN = "world.menu_login.UnloggedinCmdSet"
CONNECTION_SCREEN_MODULE = "world.menu_login.connection_screens"

# 设置账号密码最小长度为2
MIN_USERNAME_LENGTH = 2
MIN_PASSWORD_LENGTH = 2

# 自定义用户名验证器
USERNAME_VALIDATORS = [
    {"NAME": "django.contrib.auth.validators.ASCIIUsernameValidator"},
    {"NAME": "django.core.validators.MinLengthValidator", "OPTIONS": {"limit_value": 2}},
    {"NAME": "django.core.validators.MaxLengthValidator", "OPTIONS": {"limit_value": 30}},
    {"NAME": "evennia.server.validators.EvenniaUsernameAvailabilityValidator"},
]

# 自定义密码验证器
ACCOUNT_PASSWORD_VALIDATORS = [
    {"NAME": "django.core.validators.MinLengthValidator", "OPTIONS": {"limit_value": 2}},
]
# 禁用密码强度检查
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
# 禁用用户名和密码验证规则
ACCOUNT_VALIDATORS = []

# Setname命令配置
SETNAME_MAX_USES = 88  # 每个角色可以使用setname命令的最大次数，设置为1表示只能使用一次


######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")