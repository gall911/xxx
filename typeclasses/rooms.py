"""
房间类型类
"""
from evennia import DefaultRoom

class Room(DefaultRoom):
    """
    修仙世界的房间
    """
    
    def at_object_creation(self):
        """初始化"""
        super().at_object_creation()
        self.db.safe_zone = False
    
    def return_appearance(self, looker, **kwargs):
        """
        【核心修改】完全接管 'look' 的显示结果
        """
        if not looker: return ""

        # 1. 标题 (青色)
        title = f"|c{self.get_display_name(looker)}|n(#{self.id})"
        
        # 2. 描述
        desc = self.db.desc if self.db.desc else "这里一片混沌。"
        
        # 3. 分类整理房间里的东西
        # 拿到所有能看见的东西
        visible = [obj for obj in self.contents if obj != looker and obj.access(looker, "view")]
        
        exits = []   # 出口
        users = []   # 玩家
        npcs = []    # NPC
        items = []   # 物品
        
        for obj in visible:
            if obj.destination:
                exits.append(obj)
            elif obj.has_account:
                users.append(obj)
            # 判断是否为NPC (兼容 is_npc 属性或 tag)
            elif (hasattr(obj, 'is_npc') and obj.is_npc) or obj.tags.get("npc"):
                npcs.append(obj)
            else:
                items.append(obj)

        # === 拼装文本 ===
        text = f"{title}\n{desc}\n"

        # 4. 显示安全区标记
        if self.db.safe_zone:
            text += "\n|g【安全区】|n"

        # 5. 显示出口 (修改：仅显示方向链接，不带描述)
        if exits:
            text += "\n|w【出口】|n"
            exit_list = []
            for ex in exits:
                # |lc<命令>|lt<显示文字>|le
                # 点击 exit.key (如 north) 自动执行该命令
                exit_key = ex.key
                link = f"|lc{exit_key}|lt{exit_key}|le"
                exit_list.append(link)
            
            text += " " + " ".join(exit_list) + "\n"

        # 6. 显示 NPC 和 玩家 (修改：中文名(英文Key链接))
        chars = users + npcs
        if chars:
            text += "\n|y【这里有】|n"
            for char in chars:
                # 获取中文名逻辑：
                # 1. 如果有 db.cname (自定义中文名属性)，优先使用
                # 2. 否则使用 db.name (如果有)
                # 3. 最后使用 get_display_name()
                if char.db.cname:
                    cn_name = char.db.cname
                elif char.db.name:
                     # 有些架构将中文名存在db.name，英文名仅作key
                    cn_name = char.db.name
                else:
                    cn_name = char.get_display_name(looker)

                # 获取英文ID (key)
                en_key = char.key
                
                # 构建显示: 中文名(|lclook 英文名|lt英文名|le)
                # 注意：链接点击执行 look <key>
                line = f"\n  {cn_name}(|lclook {en_key}|lt{en_key}|le)"
                
                # 显示血量
                if hasattr(char.ndb, 'hp') and char.ndb.max_hp:
                    pct = int(char.ndb.hp / char.ndb.max_hp * 100)
                    line += f" |x(HP:{pct}%)|n"
                
                text += line

        # 7. 显示物品
        if items:
            text += "\n\n|g【物品】|n"
            for item in items:
                # 物品也采用类似逻辑
                cn_name = item.db.cname if item.db.cname else item.get_display_name(looker)
                en_key = item.key
                # 物品点击可能是 look 或 get，这里默认 look
                line = f"\n  {cn_name}(|lclook {en_key}|lt{en_key}|le)"
                text += line

        return text
