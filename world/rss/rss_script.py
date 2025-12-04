import os
import yaml
import feedparser
import random
from django.conf import settings
from evennia import DefaultScript
from evennia.utils import utils, create
from evennia.comms.models import ChannelDB
from evennia.server.sessionhandler import SESSIONS

# 配置文件路径
CONFIG_PATH = os.path.join(settings.GAME_DIR, "world", "rss", "config.yaml")

class RSSBroadcaster(DefaultScript):
    """
    这是一个修仙风格的RSS广播脚本。
    它会定期轮询配置中的RSS源，并广播最新的一条新闻。
    """

    def at_script_creation(self):
        self.key = "rss_broadcaster"
        self.desc = "Broadcasting RSS feeds in Xiu Xian style"
        self.interval = 300  # 每300秒(5分钟)检查一次，可自行调整
        self.persistent = True
        
        # 存储状态
        self.db.last_guids = {} # 记录每个源已发送过的最新文章ID {url: last_guid}
        self.db.feed_index = 0  # 用于轮询多源

    def load_config(self):
        """加载 YAML 配置"""
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            utils.to_str(f"RSS Script Error loading config: {e}")
            return None

    def get_channel_or_broadcast(self, channel_name, config):
        """
        尝试获取频道，如果获取失败，根据配置决定是否全服广播
        返回: (callable_method, is_channel_object)
        """
        # 1. 尝试获取指定频道
        chan = ChannelDB.objects.get_channel(channel_name)
        if chan:
            return chan.msg, True
        
        # 2. 尝试获取默认频道
        default_name = config.get("default_channel", "Public")
        chan = ChannelDB.objects.get_channel(default_name)
        if chan:
            return chan.msg, True

        # 3. 最后的手段：全服系统广播 (System Broadcast)
        if config.get("system_broadcast_fallback", True):
            return SESSIONS.announce_all, False
        
        return None, False

    def fetch_feed_task(self, url):
        """
        这是在异步线程中运行的函数，负责下载和解析
        """
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                return feed.entries[0] # 返回最新的一条
        except Exception as e:
            return None
        return None

    def format_xiuxian_msg(self, entry, config):
        """将新闻包装成修仙风格"""
        prefixes = config.get("prefixes", ["【天道】"])
        prefix = random.choice(prefixes)
        
        title = entry.get('title', '无名天书')
        link = entry.get('link', '')
        
        # 组装消息
        # 这里的颜色代码 |w, |n 是 Evennia 的标准颜色代码
        msg = f"\n|r{prefix}|n\n|w“{title}”|n\n|g[详情请观玉简]: {link}|n"
        return msg

    def _callback(self, entry, feed_config, config):
        """异步抓取完成后的回调"""
        if not entry:
            return

        url = feed_config['url']
        guid = entry.get('id', entry.get('link')) # 获取唯一标识
        
        # 检查是否已经发过这条
        last_guid = self.db.last_guids.get(url)
        if last_guid == guid:
            # 这一条已经广播过了，无事发生
            return

        # 更新已读记录
        self.db.last_guids[url] = guid
        
        # 格式化消息
        message = self.format_xiuxian_msg(entry, config)
        
        # 发送消息
        target_channel = feed_config.get('target_channel')
        sender, is_channel = self.get_channel_or_broadcast(target_channel, config)
        
        if sender:
            if is_channel:
                # 频道发送通常不需要 msg=... 格式，直接传参即可，或者 send=...
                # 但为了保险，使用 standard msg
                sender(message)
            else:
                # SESSIONS.announce_all 直接接受字符串
                sender(message)

    def at_repeat(self):
        """每隔 interval 秒运行一次"""
        config = self.load_config()
        if not config or not config.get('feeds'):
            return

        feeds = [f for f in config['feeds'] if f.get('enabled', True)]
        if not feeds:
            return

        # 轮询逻辑：获取当前索引的源
        idx = self.db.feed_index % len(feeds)
        current_feed = feeds[idx]
        
        # 指向下一个，供下次使用
        self.db.feed_index += 1

        # 异步执行抓取，避免卡死主游戏循环
        utils.run_async(
            self.fetch_feed_task,
            current_feed['url'],
            callback=self._callback,
            feed_config=current_feed,
            config=config
        )