"""
A login menu using EvMenu.
FIXED: Removed global imports to prevent RuntimeWarning.
"""

from django.conf import settings
from evennia import CmdSet, Command, syscmdkeys
from evennia.utils.evmenu import EvMenu
from evennia.utils.utils import (
    callables_from_module,
    class_from_module,
    random_string_from_module,
)

_ACCOUNT_HELP = "Enter a new or existing login name."
_PASSWORD_HELP = (
    "Password should be a minimum of 8 characters (preferably longer) and "
    "can contain a mix of letters, spaces, digits and @/./+/-/_/'/, only."
)

def _get_account_class():
    return class_from_module(settings.BASE_ACCOUNT_TYPECLASS)

def _get_guest_class():
    return class_from_module(settings.BASE_GUEST_TYPECLASS)

def _show_help(caller, raw_string, **kwargs):
    help_entry = kwargs["help_entry"]
    caller.msg(help_entry)
    return None

def node_enter_username(caller, raw_text, **kwargs):
    """Start node of menu"""
    
    # 获取配置
    GUEST_ENABLED = settings.GUEST_ENABLED
    CONNECTION_SCREEN_MODULE = settings.CONNECTION_SCREEN_MODULE
    Account = _get_account_class()
    Guest = _get_guest_class()

    def _check_input(caller, username, **kwargs):
        username = username.rstrip("\n")

        if username == "guest" and GUEST_ENABLED:
            session = caller
            address = session.address
            account, errors = Guest.authenticate(ip=address)
            if account:
                return "node_quit_or_login", {"login": True, "account": account}
            else:
                session.msg("|R{}|n".format("\n".join(errors)))
                return None

        # 检查用户名长度
        if len(username) < 2:
            caller.msg("|r用户名太短了，请至少输入2个字符。|n")
            return None

        try:
            Account.objects.get(username__iexact=username)
        except Account.DoesNotExist:
            new_user = True
        else:
            new_user = False

        if new_user and not settings.NEW_ACCOUNT_REGISTRATION_ENABLED:
            caller.msg("Registration is currently disabled.")
            return None

        return "node_enter_password", {"new_user": new_user, "username": username}

    callables = callables_from_module(CONNECTION_SCREEN_MODULE)
    if "connection_screen" in callables:
        connection_screen = callables["connection_screen"]()
    else:
        connection_screen = random_string_from_module(CONNECTION_SCREEN_MODULE)

    if GUEST_ENABLED:
        text = "Enter a new or existing user name to login (write 'guest' for a guest login):"
    else:
        text = "Enter a new or existing user name to login:"
    text = "{}\n\n{}".format(connection_screen, text)

    options = (
        {"key": "", "goto": "node_enter_username"},
        {"key": ("quit", "q"), "goto": "node_quit_or_login"},
        {"key": ("help", "h"), "goto": (_show_help, {"help_entry": _ACCOUNT_HELP, **kwargs})},
        {"key": "_default", "goto": _check_input},
    )
    return text, options

def node_enter_password(caller, raw_string, **kwargs):
    """Handle password input."""
    
    Account = _get_account_class()

    def _check_input(caller, password, **kwargs):
        username = kwargs["username"]
        new_user = kwargs["new_user"]
        password = password.rstrip("\n")

        session = caller
        address = session.address
        if new_user:
            account, errors = Account.create(
                username=username, password=password, ip=address, session=session
            )
        else:
            account, errors = Account.authenticate(
                username=username, password=password, ip=address, session=session
            )

        if account:
            if new_user:
                session.msg("|gA new account |c{}|g was created. Welcome!|n".format(username))
            return "node_quit_or_login", {"login": True, "account": account}
        else:
            session.msg("|R{}".format("\n".join(errors)))
            kwargs["retry_password"] = True
            return "node_enter_password", kwargs

    def _restart_login(caller, *args, **kwargs):
        caller.msg("|yCancelled login.|n")
        return "node_enter_username"

    username = kwargs["username"]
    if kwargs["new_user"]:
        if kwargs.get("retry_password"):
            text = "Enter a new password:"
        else:
            text = "Creating a new account |c{}|n. Enter a password (empty to abort):".format(username)
    else:
        text = "Enter the password for account |c{}|n (empty to abort):".format(username)
    
    options = (
        {"key": "", "goto": _restart_login},
        {"key": ("quit", "q"), "goto": "node_quit_or_login"},
        {"key": ("help", "h"), "goto": (_show_help, {"help_entry": _PASSWORD_HELP, **kwargs})},
        {"key": "_default", "goto": (_check_input, kwargs)},
    )
    return text, options

def node_quit_or_login(caller, raw_text, **kwargs):
    session = caller
    if kwargs.get("login"):
        account = kwargs.get("account")
        session.msg("|gLogging in ...|n")
        session.sessionhandler.login(session, account)
    else:
        session.sessionhandler.disconnect(session, "Goodbye! Logging off.")
    return "", {}

class MenuLoginEvMenu(EvMenu):
    def node_formatter(self, nodetext, optionstext):
        return nodetext
    def options_formatter(self, optionlist):
        return ""

class UnloggedinCmdSet(CmdSet):
    key = "DefaultUnloggedin"
    priority = 0
    def at_cmdset_creation(self):
        self.add(CmdUnloggedinLook())

class CmdUnloggedinLook(Command):
    key = syscmdkeys.CMD_LOGINSTART
    locks = "cmd:all()"
    arg_regex = r"^$"
    def func(self):
        menu_nodes = {
            "node_enter_username": node_enter_username,
            "node_enter_password": node_enter_password,
            "node_quit_or_login": node_quit_or_login,
        }
        MenuLoginEvMenu(
            self.caller,
            menu_nodes,
            startnode="node_enter_username",
            auto_look=False,
            auto_quit=False,
            cmd_on_exit=None,
        )