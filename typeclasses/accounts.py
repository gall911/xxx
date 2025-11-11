"""
Account

The Account represents the game "account" and each login has only one
Account object. An Account is what chats on default channels but has no
other in-game-world existence. Rather the Account puppets Objects (such
as Characters) in order to actually participate in the game world.


Guest

Guest accounts are simple low-level accounts that are created/deleted
on the fly and allows users to test the game without the commitment
of a full registration. Guest accounts are deactivated by default; to
activate them, add the following line to your settings file:

    GUEST_ENABLED = True

You will also need to modify the connection screen to reflect the
possibility to connect with a guest account. The setting file accepts
several more options for customizing the Guest account system.

"""

from evennia.accounts.accounts import DefaultAccount, DefaultGuest
from django.conf import settings


class Account(DefaultAccount):
    """
    An Account is the actual OOC player entity. It doesn't exist in the game,
    but puppets characters.

    This is the base Typeclass for all Accounts. Accounts represent
    the person playing the game and tracks account info, password
    etc. They are OOC entities without presence in-game. An Account
    can connect to a Character Object in order to "enter" the
    game.

    Account Typeclass API:

    * Available properties (only available on initiated typeclass objects)

     - key (string) - name of account
     - name (string)- wrapper for user.username
     - aliases (list of strings) - aliases to the object. Will be saved to
            database as AliasDB entries but returned as strings.
     - dbref (int, read-only) - unique #id-number. Also "id" can be used.
     - date_created (string) - time stamp of object creation
     - permissions (list of strings) - list of permission strings
     - user (User, read-only) - django User authorization object
     - obj (Object) - game object controlled by account. 'character' can also
                     be used.
     - is_superuser (bool, read-only) - if the connected user is a superuser

    * Handlers

     - locks - lock-handler: use locks.add() to add new lock strings
     - db - attribute-handler: store/retrieve database attributes on this
                              self.db.myattr=val, val=self.db.myattr
     - ndb - non-persistent attribute handler: same as db but does not
                                  create a database entry when storing data
     - scripts - script-handler. Add new scripts to object with scripts.add()
     - cmdset - cmdset-handler. Use cmdset.add() to add new cmdsets to object
     - nicks - nick-handler. New nicks with nicks.add().
     - sessions - session-handler. Use session.get() to see all sessions connected, if any
     - options - option-handler. Defaults are taken from settings.OPTIONS_ACCOUNT_DEFAULT
     - characters - handler for listing the account's playable characters

    * Helper methods (check autodocs for full updated listing)

     - msg(text=None, from_obj=None, session=None, options=None, **kwargs)
     - execute_cmd(raw_string)
     - search(searchdata, return_puppet=False, search_object=False, typeclass=None,
                      nofound_string=None, multimatch_string=None, use_nicks=True,
                      quiet=False, **kwargs)
     - is_typeclass(typeclass, exact=False)
     - swap_typeclass(new_typeclass, clean_attributes=False, no_default=True)
     - access(accessing_obj, access_type='read', default=False, no_superuser_bypass=False, **kwargs)
     - check_permstring(permstring)
     - get_cmdsets(caller, current, **kwargs)
     - get_cmdset_providers()
     - uses_screenreader(session=None)
     - get_display_name(looker, **kwargs)
     - get_extra_display_name_info(looker, **kwargs)
     - disconnect_session_from_account()
     - puppet_object(session, obj)
     - unpuppet_object(session)
     - unpuppet_all()
     - get_puppet(session)
     - get_all_puppets()
     - is_banned(**kwargs)
     - get_username_validators(validator_config=settings.AUTH_USERNAME_VALIDATORS)
     - authenticate(username, password, ip="", **kwargs)
     - normalize_username(username)
     - validate_username(username)
     - validate_password(password, account=None)
     - set_password(password, **kwargs)
     - get_character_slots()
     - get_available_character_slots()
     - create_character(*args, **kwargs)
     - create(*args, **kwargs)
     - delete(*args, **kwargs)
     - channel_msg(message, channel, senders=None, **kwargs)
     - idle_time()
     - connection_time()

    * Hook methods

     basetype_setup()
     at_account_creation()

     > note that the following hooks are also found on Objects and are
       usually handled on the character level:

     - at_init()
     - at_first_save()
     - at_access()
     - at_cmdset_get(**kwargs)
     - at_password_change(**kwargs)
     - at_first_login()
     - at_pre_login()
     - at_post_login(session=None)
     - at_failed_login(session, **kwargs)
     - at_disconnect(reason=None, **kwargs)
     - at_post_disconnect(**kwargs)
     - at_message_receive()
     - at_message_send()
     - at_server_reload()
     - at_server_shutdown()
     - at_look(target=None, session=None, **kwargs)
     - at_post_create_character(character, **kwargs)
     - at_post_add_character(char)
     - at_post_remove_character(char)
     - at_pre_channel_msg(message, channel, senders=None, **kwargs)
     - at_post_chnnel_msg(message, channel, senders=None, **kwargs)

    """

    def at_account_creation(self):
        """
        创建账户时初始化first_name和last_name属性
        """
        super().at_account_creation()
        # 初始化中文名属性
        self.db.first_name = ""
        self.db.last_name = ""
        # 初始化性别属性（默认未设置）
        self.db.gender = ""
        # 初始化setname命令使用次数
        self.db.setname_used_count = 0
    
    @property
    def first_name(self):
        """
        获取名字
        
        Returns:
            str: 名字
        """
        return self.db.first_name if hasattr(self.db, "first_name") else ""
    
    @property
    def last_name(self):
        """
        获取姓氏
        
        Returns:
            str: 姓氏
        """
        return self.db.last_name if hasattr(self.db, "last_name") else ""
    
    def set_name(self, first_name="", last_name=""):
        """
        设置中文名
        
        Args:
            first_name (str): 名字
            last_name (str): 姓氏
        """
        self.db.first_name = first_name
        self.db.last_name = last_name
    
    @property
    def gender(self):
        """
        获取性别
        
        Returns:
            str: 性别（男/女/其他）
        """
        return self.db.gender if hasattr(self.db, "gender") else ""
    
    def set_gender(self, gender=""):
        """
        设置性别
        
        Args:
            gender (str): 性别（男/女/其他）
        """
        valid_genders = ["男", "女", "其他"]
        if gender in valid_genders:
            self.db.gender = gender
        else:
            raise ValueError(f"无效的性别：{gender}，请使用：{', '.join(valid_genders)}")
    
    def get_chinese_name(self):
        """
        获取完整的中文名
        
        Returns:
            str: 完整的中文名（姓氏+名字）
        """
        if self.first_name and self.last_name:
            return f"{self.last_name}{self.first_name}"
        return ""
    
    def can_set_name(self):
        """
        检查是否可以使用setname命令
        
        Returns:
            bool: 如果可以使用返回True，否则返回False
        """
        max_uses = getattr(settings, "SETNAME_MAX_USES", 1)
        current_count = self.db.setname_used_count if hasattr(self.db, "setname_used_count") else 0
        # 确保current_count是整数，避免NoneType错误
        if current_count is None:
            current_count = 0
        return current_count < max_uses
    
    def mark_setname_used(self):
        """
        标记setname命令已被使用一次
        """
        current_count = self.db.setname_used_count if hasattr(self.db, "setname_used_count") else 0
        # 确保current_count是整数，避免NoneType错误
        if current_count is None:
            current_count = 0
        self.db.setname_used_count = current_count + 1
    
    def get_setname_remaining_uses(self):
        """
        获取setname命令剩余使用次数
        
        Returns:
            int: 剩余使用次数
        """
        max_uses = getattr(settings, "SETNAME_MAX_USES", 1)
        current_count = self.db.setname_used_count if hasattr(self.db, "setname_used_count") else 0
        # 确保current_count是整数，避免NoneType错误
        if current_count is None:
            current_count = 0
        return max(0, max_uses - current_count)


class Guest(DefaultGuest):
    """
    This class is used for guest logins. Unlike Accounts, Guests and their
    characters are deleted after disconnection.
    """

    pass