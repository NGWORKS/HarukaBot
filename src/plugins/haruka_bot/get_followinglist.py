from nonebot import require
from nonebot.log import logger
from .utils import scheduler
import asyncio,json,httpx
from .config import Config
from .login_manage import BiliApi
from .utils import safe_send, scheduler
import math
@scheduler.scheduled_job('cron', minute='*/5', id='get_followinglist')
async def get_followinglist():
    b = BiliApi()
    # 预先请求
    follow_list = await b.get_follow_list(1)
    print(follow_list)
    count = int(follow_list['count'])

    
    if count == 0:
        logger.warning(f"你的账号并没有关注任何人，账号列表模式将不可用，正在同步订阅列表...")
    else:
        data_list = follow_list['data']
        if count > 50:
            page = math.ceil(count/50)
            i = 2
            newlist = []
            name1 = follow_list['name']
            while i < page + 1:
                followlist = await b.get_follow_list(i)
                newlist = newlist + followlist['data']
                name2 = followlist['name']
                name1.update(name2)
                i = i + 1
            newlist = newlist + data_list
            follow_list = newlist
            name = name1

        else:
            name = follow_list['name']
            follow_list = data_list
        hblist = await Config().get_all_uid_list()
        #在bilibili列表中而不在hb列表中
        c = [x for x in follow_list if x not in hblist]
        #在hb列表中而不在bilibili列表中
        d = [y for y in hblist if y not in follow_list]
        for dt in c:
            uname = name[dt]
            data = await Config().test_add_uid(dt,uname)
            logger.debug(f"同步关注哔哩哔哩 {uname}")