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



######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")

# 2. 用于设置【密码】最小长度为 2 (同时保留其他验证)
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 2  # 允许最小长度为 2
        }
    },
    # 删除了 UserAttributeSimilarityValidator
    # 删除了 CommonPasswordValidator
    # 删除了 NumericPasswordValidator
]
AUTH_USERNAME_VALIDATORS = []
ACCOUNT_USERNAME_MIN_LENGTH = 2
ACCOUNT_USERNAME_MAX_LENGTH = 30
TIME_ZONE = 'Asia/Shanghai'
USE_TZ = True

USERNAME_VALIDATOR = None

