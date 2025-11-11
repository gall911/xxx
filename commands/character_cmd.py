from evennia.commands.default.muxcommand import MuxCommand as Command
from evennia.utils.evmenu import EvMenu
from django.conf import settings

class CmdCharacter(Command):
    """
    修仙角色设定 - 以问答方式设定你的修仙角色
    
    用法:
      character - 开始角色设定流程
      character info - 查看当前角色信息
      character gender <性别> - 单独设置性别
    
    此命令将引导你完成修仙角色的基本设定，包括姓名、性别等。
    每个角色只能完成一次完整的设定，请谨慎选择。
    """
    
    key = "character"
    aliases = ["角色", "char", "setname","setuser"]
    help_category = "修仙"
    
    def func(self):
        if not self.args:
            # 开始角色设定流程
            self.start_character_setup()
            return
            
        # 解析参数
        parts = self.args.strip().split()
        
        if parts[0].lower() == "info":
            # 查看角色信息
            self.show_character_info()
            return
            
        elif parts[0].lower() == "gender":
            # 单独设置性别
            if len(parts) < 2:
                self.msg("|r用法错误|n: 请提供性别，例如 |y角色 gender 男|n")
                return
                
            gender = parts[1].strip()
            try:
                self.caller.account.set_gender(gender)
                self.msg(f"|g性别设定成功！|n 你的性别现在是 |c{gender}|n")
            except ValueError as e:
                self.msg(f"|r错误|n: {e}")
            return
            
        else:
            self.msg("|r未知命令|n: 使用 |y角色|n 开始角色设定，或 |y角色 info|n 查看当前信息。")
    
    def start_character_setup(self):
        """开始修仙角色设定流程（使用EvMenu）"""
        
        # 检查是否已经完成设定
        if not self.caller.account.can_set_name():
            max_uses = getattr(settings, "SETNAME_MAX_USES", 1)
            self.msg(f"|r天机已定|n: 每个修仙者只能设定角色 {max_uses} 次，无法再次修改。")
            return
        
        # 使用EvMenu开始角色设定流程
        EvMenu(self.caller, "commands.character_cmd", 
               startnode="character_setup_menu", 
               cmdset_mergetype="Replace",
               persistent=False)
    

    
    def show_character_info(self):
        """显示角色信息"""
        first_name = self.caller.account.first_name
        last_name = self.caller.account.last_name
        gender = self.caller.account.gender
        
        if first_name and last_name:
            self.msg("\n|c【角色信息】|n")
            self.msg(f"|w姓名|n: {last_name}{first_name}")
            if gender:
                self.msg(f"|w性别|n: {gender}")
            else:
                self.msg("|w性别|n: |y未设定|n")
            
            remaining_uses = self.caller.account.get_setname_remaining_uses()
            if remaining_uses > 0:
                self.msg(f"|w剩余设定次数|n: {remaining_uses}")
            else:
                self.msg("|w设定状态|n: |r已锁定|n (天机已定)")
        else:
            self.msg("|y尚未完成角色设定|n: 使用 |g角色|n 命令开始设定。")
    



# 为了向后兼容，保留原来的setname命令
class CmdSetName(CmdCharacter):
    """setname命令的别名（向后兼容）"""
    
    key = "setname"
    aliases = []
    help_category = "修仙"


# EvMenu 角色设定菜单
def character_setup_menu(caller, raw_string, **kwargs):
    """角色设定菜单入口"""
    
    text = """|c═══════════════════════════════════════|n
|y        修仙角色设定|n
|c═══════════════════════════════════════|n

|w欢迎来到修仙世界，请设定你的角色|n
|w此设定将影响你的修仙之路|n
|w请谨慎选择，|r天机不可逆|n|w|n

|y提示|n: 请直接输入内容回答问题，无需使用命令
"""
    
    options = (
        {
            "key": "_default",
            "goto": ("node_ask_surname", kwargs)
        },
    )
    
    return text, options


def node_ask_surname(caller, raw_string, **kwargs):
    """询问姓氏"""
    
    text = """|c═══════════════════════════════════════|n
|y【第一问】|w 道友姓氏|n
|c═══════════════════════════════════════|n

|w请告知你的姓氏：|n

|y提示|n: 直接输入你的姓氏即可
"""
    
    options = (
        {
            "key": "_default",
            "goto": ("node_process_surname", kwargs)
        },
    )
    
    return text, options


def node_process_surname(caller, raw_string, **kwargs):
    """处理姓氏输入"""
    
    surname = raw_string.strip()
    
    # 验证姓氏
    if not surname:
        caller.msg("|r姓氏不能为空|n，请重新输入：")
        return node_ask_surname(caller, raw_string, **kwargs)
    
    if len(surname) > 10:
        caller.msg("|r姓氏过长|n，请控制在10个字符以内：")
        return node_ask_surname(caller, raw_string, **kwargs)
    
    # 保存姓氏
    caller.ndb.temp_surname = surname
    
    # 转到询问名字
    return node_ask_given_name(caller, raw_string, surname=surname)


def node_ask_given_name(caller, raw_string, **kwargs):
    """询问名字"""
    
    surname = kwargs.get("surname", "")
    
    text = """|c═══════════════════════════════════════|n
|y【第二问】|w {surname}氏族人之名|n
|c═══════════════════════════════════════|n

|w{surname}氏族人，请告知你的名字：|n

|y提示|n: 直接输入你的名字即可
""".format(surname=surname)
    
    options = (
        {
            "key": "_default",
            "goto": ("node_process_given_name", kwargs)
        },
    )
    
    return text, options


def node_process_given_name(caller, raw_string, **kwargs):
    """处理名字输入"""
    
    given_name = raw_string.strip()
    
    # 验证名字
    if not given_name:
        caller.msg("|r名字不能为空|n，请重新输入：")
        return node_ask_given_name(caller, raw_string, **kwargs)
    
    if len(given_name) > 20:
        caller.msg("|r名字过长|n，请控制在20个字符以内：")
        return node_ask_given_name(caller, raw_string, **kwargs)
    
    # 保存名字
    caller.ndb.temp_given_name = given_name
    
    # 转到询问性别
    return node_ask_gender(caller, raw_string)


def node_ask_gender(caller, raw_string, **kwargs):
    """询问性别"""
    
    given_name = caller.ndb.temp_given_name
    
    text = """|c═══════════════════════════════════════|n
|y【第三问】|w {given_name}道友之性別|n
|c═══════════════════════════════════════|n

|w{given_name}道友，请选择你的性别：|n

|g1|n. |w男|n - 阳刚之气，适合修炼刚猛功法
|g2|n. |w女|n - 阴柔之体，适合修炼灵巧功法
|g3|n. |w其他|n - 阴阳调和，适合修炼平衡功法

|y提示|n: 请输入 |g1|n、|g2|n 或 |g3|n 来选择性别
""".format(given_name=given_name)
    
    options = (
        {
            "key": "_default",
            "goto": ("node_process_gender", kwargs)
        },
    )
    
    return text, options


def node_process_gender(caller, raw_string, **kwargs):
    """处理性别选择"""
    
    choice = raw_string.strip()
    
    # 验证性别选择
    gender_map = {"1": "男", "2": "女", "3": "其他"}
    gender = gender_map.get(choice)
    
    if not gender:
        caller.msg("|r选择无效|n: 请选择 1、2 或 3")
        return node_ask_gender(caller, raw_string)
    
    # 完成角色设定
    return node_complete_setup(caller, raw_string, gender=gender)


def node_complete_setup(caller, raw_string, gender=None, **kwargs):
    """完成角色设定"""
    
    # 如果gender没有通过参数传递，尝试从kwargs获取
    if gender is None:
        gender = kwargs.get("gender")
    surname = caller.ndb.temp_surname
    given_name = caller.ndb.temp_given_name
    
    # 设置姓名
    caller.account.set_name(given_name, surname)
    
    # 设置性别
    try:
        caller.account.set_gender(gender)
    except ValueError as e:
        caller.msg(f"|r性别设定失败|n: {e}")
        return node_ask_gender(caller, raw_string)
    
    # 标记设定完成
    caller.account.mark_setname_used()
    
    # 显示设定结果 - 使用更简洁的格式
    text = """|c═══════════════════════════════════════|n
|y        角色设定完成|n
|y═══════════════════════════════════════|n

|w道友信息：|n
  |g姓名：|w{surname}{given_name}|n
  |g性别：|w{gender}|n

|g恭喜道友踏上修仙之路！|n
|g愿你在修真界闯出一片天地|n

|c═══════════════════════════════════════|n
""".format(surname=surname, given_name=given_name, gender=gender)
    
    # 清理临时数据
    if hasattr(caller.ndb, 'temp_surname'):
        del caller.ndb.temp_surname
    if hasattr(caller.ndb, 'temp_given_name'):
        del caller.ndb.temp_given_name
    
    # 结束菜单
    return text, ()