# typeclasses/asset_handler.py

class AssetHandler:
    """
    资产管理器：处理无需实体的数值型物品（金币、材料）。
    数据存储: self.owner.db.assets = {'gold': 100, 'iron_ore': 50}
    """
    def __init__(self, owner):
        self.owner = owner

    @property
    def _data(self):
        """获取底层字典，懒加载"""
        if self.owner.db.assets is None:
            self.owner.db.assets = {}
        return self.owner.db.assets

    def get_amount(self, key):
        """查询数量"""
        return self._data.get(key, 0)

    def add(self, key, amount=1):
        """增加资产"""
        if amount <= 0: return
        current = self.get_amount(key)
        self._data[key] = current + amount
        # 这里的提示信息通常由调用层处理，Handler保持纯净

    def consume(self, key, amount=1):
        """消耗资产"""
        if amount <= 0: return False
        current = self.get_amount(key)
        if current < amount:
            return False
        
        self._data[key] = current - amount
        return True

    def display(self):
        """返回格式化的资源列表字符串"""
        if not self._data:
            return "你的资源包是空的。"
        
        lines = ["|w[ 资源/材料 ]|n"]
        # 使用 sorted 保证显示顺序固定
        for key, val in sorted(self._data.items()):
            if val > 0:
                lines.append(f"  {key:<15}: |g{val}|n")
        return "\n".join(lines)