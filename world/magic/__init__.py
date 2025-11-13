# 魔法系统主包

def init_magic_system():
    """
    初始化魔法系统
    """
    try:
        from evennia import create_script
        from world.magic.magic_system import MagicSystem
        
        # 检查魔法系统脚本是否存在
        magic_system = create_script(MagicSystem, key="magic_system")
        print(f"魔法系统脚本已创建: {magic_system}")
        
        # 初始化帮助条目
        try:
            from world.help_entries.magic_help import create_magic_help_entries
            from evennia import create_help_entry
            
            help_entries = create_magic_help_entries()
            print(f"创建了 {len(help_entries)} 个帮助条目")
            for entry in help_entries:
                # 确保所有必要的键都存在
                if "key" not in entry:
                    print(f"帮助条目缺少键: {entry}")
                    continue
                if "entrytext" not in entry:
                    print(f"帮助条目 {entry['key']} 缺少entrytext")
                    continue
                
                # 设置默认值
                if "category" not in entry:
                    entry["category"] = "魔法"
                if "locks" not in entry:
                    entry["locks"] = "view:all()"
                    
                try:
                    # Evennia 的 create_help_entry 函数期望参数名为 "text" 而不是 "entry_text"
                    if "entry_text" in entry:
                        entry["text"] = entry.pop("entry_text")
                    create_help_entry(**entry)
                    print(f"成功创建帮助条目: {entry['key']}")
                except Exception as e:
                    print(f"创建帮助条目 {entry['key']} 时出错: {e}")
        except Exception as e:
            print(f"初始化帮助条目时出错: {e}")
        
        return magic_system
    except Exception as e:
        print(f"初始化魔法系统时出错: {e}")
        return None

# 当模块被导入时自动初始化魔法系统
print("正在初始化魔法系统...")
init_magic_system()
print("魔法系统初始化完成。")