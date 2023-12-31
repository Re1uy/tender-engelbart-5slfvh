import asyncio
import random
import string

from pyrogram.types import Message
from PIL import Image
from ddddocr import DdddOcr

from ...utils import async_partial
from ...data import get_datas
from ..lock import misty_locks
from .base import Monitor

__ignore__ = True

CC_monitor_pool = {}


class CCMonitor(Monitor):
    ocr = "digit5-teko@v1"
    lock = asyncio.Lock()

    name = "CC"
    chat_name = "EmbyCc"
    chat_keyword = r"Cc-register-[A-Za-z0-9-]+"
    bot_username = "EmbyCc_bot"
    notify_create_name = True

    async def init(self, initial=True):
        async with self.lock:
            if isinstance(self.ocr, str):
                data = []
                files = (f"{self.ocr}.onnx", f"{self.ocr}.json")
                async for p in get_datas(self.basedir, files, proxy=self.proxy, caller=self.name):
                    if p is None:
                        self.log.info(f"初始化错误: 无法下载所需文件.")
                        return False
                    else:
                        data.append(p)
                self.__class__.ocr = DdddOcr(
                    show_ad=False, import_onnx_path=str(data[0]), charsets_path=str(data[1])
                )

        CC_monitor_pool[self.client.me.id] = self
        self.captcha = None
        self.log.info(f"正在初始化 {self.name} 机器人状态.")
        wr = async_partial(self.client.wait_reply, self.bot_username)
        misty_locks.setdefault(self.client.me.id, asyncio.Lock())
        lock = misty_locks.get(self.client.me.id, None)

        async with lock:
            await self.client.send_message(self.bot_username, "/start")
            response = await wr(lambda msg: "🎈兑换注册码" in msg.text)

            if response and "🎈兑换注册码" in response.text:
                await asyncio.sleep(random.uniform(2, 4))
                await self.client.send_message(self.bot_username, "🎈兑换注册码")

                response = await wr(lambda msg: "👇请把注册码发给我" in msg.text)
                if response and "👇请把注册码发给我" in response.text:
                    await self.client.send_message(self.bot_username, self.key)

                    response = await wr(lambda msg: "🤗你输入的注册码有效！" in msg.text)
                    if response and "🤗你输入的注册码有效！" in response.text:
                        await self.client.send_message(self.bot_username, self.unique_name)

                    else:
                        self.log.warning(f"{self.name} 机器人未确认注册码的有效性")
                        return False
                else:
                    self.log.warning(f"{self.name} 机器人没有请求注册码")
                    return False
            return True 