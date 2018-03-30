# ! /usr/bin/env python
# -  *  - coding:utf-8 -  *  -
#
# ETU Ad bot V1
# Create by vast - z on 2018/2/23
# Copyright Aiesst © 2017

import time
from queue import Queue
# from multiprocessing import Process
import asyncio
from telegram.ext import Updater
from telegram.ext import CommandHandler


# Config
_super_admin = [377355186, 539410589]
_interval = 60 
_token = '549671536:AAFT7P_ywV06OASR5WQZMe7siZUbTUmaG9M'
_ad_text = "Join and get free 8888 ETU tokens worth $88\nClick https://etu.link/i/?r=00sb\n\nDon't miss it!!"

# Common data stuct
# 任务队列
tasks_queue = Queue()
# id与进程/协程对应表
running_dict = {}


class Receiver:
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id


# Begin
print("ETU ad script begin...")

# 注册updater
updater = Updater(token=_token)
dispatcher = updater.dispatcher


def send_ads(bot, chat_id):
    """
    广告发送
    """
    while True:
        try:
            bot.sendMessage(chat_id=chat_id, text=_ad_text)
        except Exception as e:
            print(e)
            break
        time.sleep(_interval)
    print("chat id {} process has err, process will exit".format(chat_id))


async def send_ads_async(bot, chat_id):
    """
    广告发送，协程发送
    """
    while True:
        try:
            bot.sendMessage(chat_id=chat_id, text=_ad_text)
        except Exception as e:
            print(e)
            break
        await asyncio.sleep(_interval)
    print("chat id {} process has err, process will exit".format(chat_id))


def command(handler, cmd=None, **kw):
    """
    装饰器，用于挂载handler
    """
    def decorater(func):
        def wrapper(*args, **kw):
            return func(*args, **kw)
        if cmd == None:
            func_handler = handler(func, **kw)
        else:
            func_handler = handler(cmd, func, **kw)
            dispatcher.add_handler(func_handler)
        return wrapper

    return decorater


@command(CommandHandler, 'etu_state')
def etu_state(bot, update):
    """
    查询机器人状态命令
    """
    bot.sendMessage(chat_id=update.message.chat_id, text="I'm running..")


@command(CommandHandler, 'etu_come')
def etu_come(bot, update):
    """
    发送广告命令
    """
    if update.message.from_user.id in _super_admin:
        chat_id = update.message.chat_id
    if chat_id not in running_dict:
        print("cmd [etu_come] ", chat_id)
        tasks_queue.put(Receiver(bot, chat_id))


@command(CommandHandler, 'etu_stop')
def etu_stop(bot, update):
    """
    停止发送广告命令
    """
    if update.message.from_user.id in _super_admin:
        chat_id = update.message.chat_id
    if chat_id in running_dict:
        print("cmd [etu_stop] ", chat_id)
        # running_dict[chat_id].terminate()# 关闭进程
        running_dict[chat_id].cancel()  # 取消协程
        del running_dict[chat_id]
        print("chat id {} process terminate".format(chat_id))


# 开始监听
updater.start_polling()


async def main(loop):
    """
    用于动态增加协程任务
    """
    while True:
        if not tasks_queue.empty():
            receiver = tasks_queue.get()
            print("create task..")
            task = loop.create_task(send_ads_async(receiver.bot, receiver.chat_id))
            running_dict[receiver.chat_id] = task
        await asyncio.sleep(1)


loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))
loop.close()

# 挂起程序，并用于增加新的进程
# while True:
#     if not tasks_queue.empty():
#         receiver = tasks_queue.get()
#         p = Process(target = send_ads, args = (receiver.bot, receiver.chat_id, ))
#         # 记录正在发广告的进程
#         running_dict[receiver.chat_id] = p
#         p.start()
