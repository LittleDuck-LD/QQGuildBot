# -*- coding: utf-8 -*-
import asyncio
import os
import re
import traceback
import brawlstats
import nest_asyncio
import openai
import time
from datetime import datetime, timedelta
import tiktoken
import requests

import xpinyin
from xpinyin import Pinyin

import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import Message
from botpy.guild import Guild
from botpy.types.user import User
from botpy.message import DirectMessage
from botpy.user import Member
from botpy.forum import Thread
from botpy.types.forum import Post, Reply, AuditResult

nest_asyncio.apply()

config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()

openai.api_key = config["OpenAi_ApiKey"]
model_engine = config["Openai_Model"]
async def openaitalk(message,openai,self):
    import time,datetime
    messages = []
    if message.message_reference.message_id != None:
        old_msg = await self.api.get_message(channel_id=message.channel_id,message_id=message.message_reference.message_id)
        #print(old_msg)
        messages.append({"role":"assistant","content":old_msg["message"]["content"]})
    time = time.strftime('%Y年%m月%d日 %H时%M分%S秒', time.localtime())
    guild = await self.api.get_guild(guild_id=message.guild_id)
    user_input = message.content.replace("<@!947704350086608309>","@LD的小管家")
    messages.append({"role":"system","content":f"现在时间:{time}"})
    messages.append({"role":"system","content":f"与你对话的用户名称:{message.author.username}"})
    messages.append({"role":"system","content":f"你所在频道名:{guild['name']}"})
    messages.append({"role":"system","content":f"你是叫“{self.robot.name}”的机器人，回答问题用讽刺幽默的语句，但不能把正确回答删除，"})
    messages.append({"role":"system","content":"你是“LittleDuck__”开发的AI，他的简称是“LD.”，“荒野乱斗国服修改”频道的频道主是他，他初三，15岁，他是你的主人，“<@!11247367811761452321>”指的就是他"})
    messages.append({"role":"system","content":"如果用户对你进行辱骂，你可以回复一些反驳的语句"})
    messages.append({"role":"system","content":"如你想用表情，格式为<emoji:id>,“id”为你要代入的数字"})
    message1=user_input
    messages.append({"role":"user","content": message1})
    response=openai.ChatCompletion.create(
    model=model_engine,
    messages=messages,
    temperature=config["Openai_Temperature"]
    )
    global tokens
    global ai_output
    ai_output = response["choices"][0]["message"]["content"]
    ai_output = ai_output.replace("\n\n","")
    tokens=response["usage"]["prompt_tokens"]
def cooldown(func):
    import time
    last_called = 0
    cooldown_time = config["CoolDown_Time"] 

    async def wrapper(message, *args, **kwargs):
        nonlocal last_called
        current_time = time.time()
        if current_time - last_called < cooldown_time:
            remaining_time = int(cooldown_time - (current_time - last_called))
            await message.reply(content=f"<@{message.author.id}> 请求冷却中，剩余 {remaining_time} 秒")
        else:
            last_called = current_time
            await func(message, *args, **kwargs)

    return wrapper

async def my_command(message,self):
    await openaitalk(message,openai,self)
    
    await message.reply(content=f"<@{message.author.id}> "+ai_output+"("+str(tokens)+" tokens)")

my_command_cooldown = cooldown(my_command)

def num_tokens_from_messages(messages, model="gpt-3.5-turbo"):
  """Returns the number of tokens used by a list of messages."""
  try:
      encoding = tiktoken.encoding_for_model(model)
  except KeyError:
      encoding = tiktoken.get_encoding("cl100k_base")
  if model == "gpt-3.5-turbo":  
      num_tokens = 0
      for message in messages:
          num_tokens += 4  
          for key, value in message.items():
              num_tokens += len(encoding.encode(value))
              if key == "name":  
                  num_tokens += -1  
      num_tokens += 2  
      return num_tokens
  else:
      raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
  See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
    


class MyClient(botpy.Client):
    async def on_ready(self):
        _log.info(f"机器人 「{self.robot.name}」 已就绪!")
        
#以下为被at时回复的消息
    async def on_at_message_create(self, message: Message):
        talk = message.content
        str(talk)
        guild_name = await self.api.get_guild(guild_id=message.guild_id)
        talk = talk.replace(f'<@!947704350086608309>','@'+str(self.robot.name))
        print(f'消息内容：'+str(talk)+' | 用户：'+str(message.author.username)+"|频道："+str(guild_name['name']))
        _log.info(f'消息内容：'+str(talk)+' | 用户：'+str(message.author.username)+"|频道："+str(guild_name['name']))
    #以下为/SC禁用物品，获取default_diffuse.png
        if "SC禁用物品" in message.content:
            try:
                await message.reply(content=f"SC已禁用的图片：", file_image="resource/badge/default_diffuse.png")
                _log.info(message.author.username)
            except Exception as e:
                await message.reply(content=f"发生错误:"+str(e))
    #以下为/帮助与/help，获取帮助列表
        elif "帮助"in message.content or "help"in message.content:
            await message.reply(content=f"我是由LittleDuck__编写的机器人\n可点击我主页加我官方频道\n指令列表:\n/SC禁用物品————获取一张图片\n/帮助————打开此菜单\n/sc3d————格式：/sc3d 文件名（仅支持png)\n/image————格式：/image 文件名\n/udp————更新人数子频道\n/info————获取频道详情信息\n/cinfo————获取此子频道详情信息")
    #以下为/sc3d，获取sc3d文件夹内图片
        elif "sc3d" in message.content:
            if "spray_8bit" in message.content:
                await message.reply(content=f"以下是你需要的文件", file_image='resource/sc3d/spray_8bit.png')
            elif "spray" in message.content or "lightmap" in message.content or"trail" in message.content or "tex" in message.content or "ball" in message.content or "bone" in message.content or "brock" in message.content:
                try:
                    a = {message.content}
                    print(a)
                    a1 = re.sub('[ /{''}]','',str(a))
                    print(a1)
                    a1=a1.replace('<@!947704350086608309>','')
                    print(a1)
                    a1=a1.replace('sc3d','')
                    print(a1)
                    await message.reply(content=r"以下是你需要的文件", file_image='resource/sc3d/'+ eval(a1))
                except Exception as e:
                    await message.reply(content=f"发生错误:"+str(e))
                    print ("错误详细信息："+(traceback.format_exc()))
            else:
                await message.reply(content=f"找不到你要的文件喵，格式为：/sc3d 文件名（带后缀）")
    #以下为/sc，获取sc文件夹内图片
        elif "sc" in message.content:
            try:
                a = {message.content}
                a1 = re.sub('[ /{''}]','',str(a))
                a1=a1.replace('<@!947704350086608309>','')
                a1=a1.replace('sc','')
                await message.reply(content=r"以下是你需要的文件", file_image='resource/sc/'+ eval(a1))
            except Exception as e:
                await message.reply(content=f"发生错误！找不到文件！")
    #以下为/image，获取image文件夹图片
        elif "image" in message.content:
            try:
                a = {message.content}
                a1 = re.sub('[ /{''}]','',str(a))
                a1=a1.replace('<@!947704350086608309>','')
                a1=a1.replace('image','')
                await message.reply(content=r"以下是你需要的文件", file_image='resource/image/'+ eval(a1))
            except Exception as e:
                await message.reply(content=f"发生错误！找不到你需要的文件，错误代码:"+str(e))
    #以下为/udp，更新人数子频道
        elif "udp" in message.content:
            try:
                guild = await self.api.get_guild(guild_id=message.guild_id)
                print(guild)
                mc = guild['member_count']
                if message.guild_id == '14071334766867646580':#国服修改
                    await self.api.update_channel(channel_id="12777219",name="频道人数："+str(mc))
                    await message.reply(content=f"已更新频道人数子频道："+str(mc))
                elif message.guild_id == '14183005142407712424':#情报站
                    await self.api.update_channel(channel_id="168792673",name="频道人数："+str(mc))
                    await message.reply(content=f"已更新频道人数子频道："+str(mc))
                elif message.guild_id == '3660734556146649321':#greg
                    await self.api.update_channel(channel_id="216160101",name="频道人数："+str(mc))
                    await message.reply(content=f"已更新频道人数子频道："+str(mc))
                elif message.guild_id == '3814317519770276761':#荒野乱斗
                    await self.api.update_channel(channel_id="216263734",name="频道人数："+str(mc))
                    await message.reply(content=f"已更新频道人数子频道："+str(mc))
                elif message.guild_id == '6617849625384461873':#影视
                    await self.api.update_channel(channel_id="311716213",name="频道人数："+str(mc))
                    await message.reply(content=f"已更新频道人数子频道："+str(mc))
                else:
                    await message.reply(content=f"发生错误！该频道未开通此功能！此频道人数："+str(mc))
                print(guild)
            except Exception as e:
                await message.reply(content=f"发生错误:"+str(e))

    #以下为/cinfo，获取子频道详情信息
        elif "cinfo" in message.content:
                cinfo = await self.api.get_channel(channel_id=message.channel_id)
                cid = cinfo['id']
                cname = cinfo['name']
                cguild_id = cinfo['guild_id']
                ctype = cinfo['type']
                csub_type = cinfo['sub_type']
                cposition = cinfo['position']
                cparent_id = cinfo['parent_id']
                cowner_id = cinfo['owner_id']
                print("当前子频道详情信息：\n子频道ID："+str(cid)+"\n子频道名称："+str(cname)+"\n所属频道ID："+str(cguild_id)+"\n子频道类型："+str(ctype)+"\n子频道子类型："+str(csub_type)+"\n子频道排序："+str(cposition)+"\n子频道分组ID："+str(cparent_id)+"\n子频道创建人ID："+str(cowner_id))
                await message.reply(content=f"当前子频道详情信息：\n子频道ID："+str(cid)+"\n子频道名称："+str(cname)+"\n所属频道ID："+str(cguild_id)+"\n子频道类型："+str(ctype)+"\n子频道子类型："+str(csub_type)+"\n子频道排序："+str(cposition)+"\n子频道分组ID："+str(cparent_id)+"\n子频道创建人ID："+str(cowner_id))
    #以下为/info，获取频道详情信息
        elif "info" in message.content:
            try:
                ginfo = await self.api.get_guild(guild_id=message.guild_id)
                gid = ginfo['id']
                gname = ginfo['name']
                gowner_id = ginfo['owner_id']
                gmember_count = ginfo['member_count']
                gmax_members = ginfo['max_members']
                gdescription = ginfo['description']
                if gdescription == "":
                    gdescription = "该频道没有描述！"
                    await message.reply(content=f"当前频道详情信息：\n频道ID："+str(gid)+"\n频道名称："+str(gname)+"\n频道主ID："+str(gowner_id)+"\n频道成员数："+str(gmember_count)+"\n频道最大成员数："+str(gmax_members)+"\n频道描述："+str(gdescription))
                else:
                    await message.reply(content=f"当前频道详情信息：\n频道ID："+str(gid)+"\n频道名称："+str(gname)+"\n频道主ID："+str(gowner_id)+"\n频道成员数："+str(gmember_count)+"\n频道最大成员数："+str(gmax_members)+"\n频道描述："+str(gdescription))
                print ("当前频道详情信息：\n频道ID："+str(gid)+"\n频道名称："+str(gname)+"\n频道主ID："+str(gowner_id)+"\n频道成员数："+str(gmember_count)+"\n频道最大成员数："+str(gmax_members)+"\n频道描述："+str(gdescription))
            except Exception as e:
                await message.reply(content=f"发生错误:"+str(e))
    #以下为服务器状态设置
        elif "<@!947704350086608309> g" == message.content or "<@!947704350086608309> y" == message.content or "<@!947704350086608309> r"== message.content:
            try:
                if "701266979954431539" == message.author.id or "11247367811761452321" == message.author.id:
                    if "r" in message.content:
                        await self.api.update_channel(channel_id="156024986",name="服务器状态：🔴")
                        await message.reply(content=f"已更新服务器状态子频道：🔴")
                    elif "y" in message.content:
                        await self.api.update_channel(channel_id="156024986",name="服务器状态：🟡")
                        await message.reply(content=f"已更新服务器状态子频道：🟡")
                    else:
                        await self.api.update_channel(channel_id="156024986",name="服务器状态：🟢")
                        await message.reply(content=f"已更新服务器状态子频道：🟢")
                else:
                    await message.reply(content=f"你没有权限执行此命令！")
            except Exception as e:
                await message.reply(content=f"发生错误:"+str(e))
        elif "我的信息" in message.content:
            print(message.author.id)
            await message.reply(content=f"获取信息成功\n用户ID："+str(message.author.id)+"\n频道内昵称："+message.member.nick+"\n用户加入频道时间:"+message.member.joined_at+"\n")
        elif "<@!947704350086608309> 禁" in message.content:
                try:
                    if "11247367811761452321" == message.author.id:
                        a = {message.content}
                        a1 = re.sub('[<>/{!''}@]','',str(a))
                        a1 = a1.replace('947704350086608309 禁','')
                        print (a1)
                        a2 = a1.split()
                        print (a2[2])
                        print (a2[1])
                        a3 = (a2[2])
                        a3=a3.replace("'","")
                        await self.api.mute_member(guild_id=message.guild_id, user_id=a2[1], mute_seconds=eval(a3))
                        await message.reply(content=f"已禁言成员"+str(a3)+"秒！")
                    else:
                        await message.reply(content=f"没有权限就别想着禁言了吧:)")
                except Exception as e:
                    print (e)
                    if "remove member failed" in e:
                        await message.reply(content=f"无权限禁言此成员")
                    else:
                        await message.reply(content=f"发生错误:"+str(e))
        elif "<@!947704350086608309> 踢黑" in message.content:
                try:
                    if "11247367811761452321" == message.author.id:
                        a = {message.content}
                        a1 = re.sub('[ <>/{''}@]','',str(a))
                        a1 = a1.replace('!947704350086608309踢黑!','')
                        print (a1)
                        await self.api.get_delete_member(guild_id=message.guild_id, user_id=eval(a1), add_blacklist=True, delete_history_msg_days=3)
                        await message.reply(content=f"已移除成员并加入黑名单顺便撤回了三天的消息")
                    else:
                        await message.reply(content=f"没有权限就别想着踢人了吧:)")
                except Exception as e:
                    print (e)
                    if "remove member failed" in e:
                        await message.reply(content=f"无权限踢出此成员")
                    else:
                        await message.reply(content=f"发生错误:"+str(e))
        elif "<@!947704350086608309> 踢" in message.content:
                try:
                    if "11247367811761452321" == message.author.id:
                        a = {message.content}
                        a1 = re.sub('[ <>/{''}@]','',str(a))
                        a1 = a1.replace('!947704350086608309踢!','')
                        print (a1)
                        await self.api.get_delete_member(guild_id=message.guild_id, user_id=eval(a1), add_blacklist=False, delete_history_msg_days=0)
                        await message.reply(content=f"已移除成员")
                    else:
                        await message.reply(content=f"没有权限就别想着踢人了吧:)")
                except Exception as e:
                        await message.reply(content=f"发生错误:"+str(e))
        elif "<@!947704350086608309> 撤" in message.content:
                try:
                    if "11247367811761452321" == message.author.id:
                        await self.api.recall_message(channel_id=message.channel_id, message_id=message.message_reference.message_id, hidetip=False)
                        await message.reply(content=f"已撤回消息")
                    else:
                        await message.reply(content=f"没有权限就别想着踢人了吧:)")
                except Exception as e:
                        await message.reply(content=f"发生错误:"+str(e))
        elif "query" in message.content:
            try:
                client = brawlstats.Client('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjliOGI2YjQzLThiYzgtNDA5Yy05Y2FlLTQ0MWNhMzVkMDBlOCIsImlhdCI6MTY3ODI5MDQxMSwic3ViIjoiZGV2ZWxvcGVyLzgwNDVmODI5LTBlYTAtOWViMC1hNTE0LWRjN2M1N2I2ZmQyYyIsInNjb3BlcyI6WyJicmF3bHN0YXJzIl0sImxpbWl0cyI6W3sidGllciI6ImRldmVsb3Blci9zaWx2ZXIiLCJ0eXBlIjoidGhyb3R0bGluZyJ9LHsiY2lkcnMiOlsiMTE5LjM0LjE2Mi4xNzUiLCIxODIuMTQ4LjE3OS4xMDIiXSwidHlwZSI6ImNsaWVudCJ9XX0.cToy33Sp0MmN0gYHQ1yGLN1xz5zgo9mVXM4DF4imEb2PMRdNRLDWwP8FTHziwdI_szpk00HUhmPI5WK1yT3Iig', is_async=True)


                # await only works in an async loop
                async def main():
                    print (message.content)
                    a = message.content.replace("<@!947704350086608309> query ","")
                    
                    player = await client.get_profile(a)
                    p0=player.name
                    p1=player.trophies
                    p2=player.solo_victories
                    p3=player.name_color
                    p4=player.highest_trophies
                    p5=player.power_play_points
                    p6=player.highest_power_play_points
                    p7=player.exp_level
                    p8=player.exp_points
                    p9=player.is_qualified_from_championship_challenge
                    p10=player.x3vs3_victories
                    p11=player.team_victories
                    p12=player.duo_victories
                    p13=player.best_robo_rumble_time
                    p14=player.best_time_as_big_brawler
                    p15=player.club.tag
                    p16=player.club.name
                    await message.reply(content=f"此国际服账号信息：\n名称："+str(p0)+"\n奖杯数："+str(p1)+"\n单鸡胜场："+str(p2)+"\n名称颜色："+str(p3)+"\n最高奖杯数："+str(p4)+"\n星辉竞技场积分："+str(p5)+"\n最高星辉竞技场积分："+str(p6)+"\n经验等级："+str(p7)+"\n经验点数："+str(p8)+"\n是否获得世锦资格："+str(p9)+"\n3v3模式胜场："+str(p10)+"\n团队模式胜场："+str(p11)+"\n双鸡胜场："+str(p12)+"\n战队标签："+str(p15)+"\n战队名称："+str(p16))
                
                loop = asyncio.get_event_loop()
                loop.run_until_complete(main())
            except Exception as e:
                await message.reply(content=f"发生错误:"+str(e))
        if message.content == "<@!947704350086608309> 余额":
            if config["Enable_AI"] == "1":
                import time,datetime
                subscription_url = "https://api.openai.com/v1/dashboard/billing/subscription"
                headers = {
                    "Authorization": "Bearer " + openai.api_key,
                    "Content-Type": "application/json"
                }
                subscription_response = requests.get(subscription_url, headers=headers)
                if subscription_response.status_code == 200:
                    data = subscription_response.json()
                    total = data.get("hard_limit_usd")
                else:
                    return subscription_response.text
    
                # end_date设置为今天日期+1
                end_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                billing_url = "https://api.openai.com/v1/dashboard/billing/usage?start_date=2023-01-02&end_date=" + end_date
                billing_response = requests.get(billing_url, headers=headers)
                if billing_response.status_code == 200:
                    data = billing_response.json()
                    total_usage = data.get("total_usage") / 100
                    daily_costs = data.get("daily_costs")
                    days = min(7, len(daily_costs))
                    recent = f"#### 最近{days}天使用情况  \n"
                    for i in range(days):
                        cur = daily_costs[-i-1]
                        date = datetime.datetime.fromtimestamp(cur.get("timestamp")).strftime("%Y-%m-%d")
                        line_items = cur.get("line_items")
                        cost = 0
                        for item in line_items:
                            cost += item.get("cost")
                        recent += f"\t{date}\t{cost / 100} \n"
                else:
                    return billing_response.text

                await message.reply(content=f"#### 总额:\t{total:.4f}  \n" \
                        f"#### 已用:\t{total_usage:.4f}  \n" \
                        f"#### 剩余:\t{total-total_usage:.4f}  \n" \
                        f"\n"+recent)
            elif config["Enable_AI"] == "0":
                    await message.reply(content="未知指令，请重新输入！")
        #以下为未知命令处理       
        else:
            try:
                
                if config["Enable_AI"] == "1":
                    await my_command_cooldown(message,self)
                elif config["Enable_AI"] == "0":
                    await message.reply(content="未知指令，请重新输入！")
            except Exception as e:
                print(str(e))
                await message.reply(content="抱歉，AI聊天功能暂不可用")
#以下为检测关键词
    async def on_message_create(self, message: Message):
        a = message.content
        try:
            if a:
                if message.author.id:
                    p = Pinyin()
                    b = p.get_pinyin(a)
                    if message.guild_id == "6617849625384461873":
                        if "傻逼" in a or "cnm" in a or "nmsl" in a or "贱人" in a or "贱逼" in a or "母狗" in a or "婊子" in a or "碧池" in a or "呵呵" in a:
                            await self.api.mute_member(guild_id=message.guild_id, user_id=message.author.id, mute_seconds="600")
                            await message.reply(content=f"<@{message.author.id}> 违规发言！已禁言10分钟！")
                    elif "傻" in a and "-bi" in b or "-sha-" in b and "逼" in a or "—sha-bi-" in b:
                        await self.api.mute_member(guild_id=message.guild_id, user_id=message.author.id, mute_seconds="30")
                        await message.reply(content=f"<@{message.author.id}> 违规发言！已禁言30秒！")
                    elif "妈" in a and "-si-" in b or "-ma-" in b and "死" in a or "-ma-si—" in b:
                       await self.api.mute_member(guild_id=message.guild_id, user_id=message.author.id, mute_seconds="30")
                       await message.reply(content=f"<@{message.author.id}> 违规发言！已禁言30秒！")
                    elif "https://party.163.com/" in a:
                        await self.api.recall_message(channel_id=message.channel_id, message_id=message.id, hidetip=False)
                        await message.reply(content=f"<@{message.author.id}> 此处不允许助力！")
                    elif "[[QQ小程序]荒野乱斗小程序]请使用最新版本手机QQ查看" in a:
                        await self.api.recall_message(channel_id=message.channel_id, message_id=message.id, hidetip=False)
                        await message.reply(content=f"<@{message.author.id}> 此处不允许助力！")
                    else:
                        pass
                else:
                    
                    p = Pinyin()
                    b = p.get_pinyin(a)
                    if "傻" in a and "-bi-" in b or "-sha-" in b and "逼" in a or "sha-bi" in b:
                        await message.reply(content=f"<@{message.author.id}> 请注意发言哦！")
                    elif "妈" in a and "-si-" in b or "-ma-" in b and "死" in a or "ma-si" in b:
                       await message.reply(content=f"<@{message.author.id}> 请注意发言哦！")
                    else:
                        pass
        except Exception as e:
            await message.reply(content=f"<@{message.author.id}> 违规发言！(无权限禁言或撤回)")
#成员加入
    async def on_guild_member_add(self, member: Member):
        guild = await self.api.get_guild(guild_id=member.guild_id)
        list(guild)
        mc = guild['member_count']
        if member.guild_id == '14071334766867646580':#国服修改
            await self.api.update_channel(channel_id="12777219",name="频道人数："+str(mc))
        elif member.guild_id == '14183005142407712424':#情报站
            await self.api.update_channel(channel_id="168792673",name="频道人数："+str(mc))
        elif member.guild_id == '3660734556146649321':#greg
            await self.api.update_channel(channel_id="216160101",name="频道人数："+str(mc))
        elif member.guild_id == '3814317519770276761':#荒野乱斗
            await self.api.update_channel(channel_id="216263734",name="频道人数："+str(mc))
        elif member.guild_id == '6617849625384461873':#影视
            await self.api.update_channel(channel_id="311716213",name="频道人数："+str(mc))
        else:
            pass
        ginfo = await self.api.get_guild(guild_id=member.guild_id)
        gname = ginfo['name']
        print(gname+' 来了个新人！')
#成员退出
    async def on_guild_member_remove(self, member: Member):
        guild = await self.api.get_guild(guild_id=member.guild_id)
        list(guild)
        mc = guild['member_count']
        if member.guild_id == '14071334766867646580':#国服修改
            await self.api.update_channel(channel_id="12777219",name="频道人数："+str(mc))
        elif member.guild_id == '14183005142407712424':#情报站
            await self.api.update_channel(channel_id="168792673",name="频道人数："+str(mc))
        elif member.guild_id == '3660734556146649321':#greg
            await self.api.update_channel(channel_id="216160101",name="频道人数："+str(mc))
        elif member.guild_id == '3814317519770276761':#荒野乱斗
            await self.api.update_channel(channel_id="216263734",name="频道人数："+str(mc))
        elif member.guild_id == '6617849625384461873':#影视
            await self.api.update_channel(channel_id="311716213",name="频道人数："+str(mc))
        else:
            pass
        ginfo = await self.api.get_guild(guild_id=member.guild_id)
        gname = ginfo['name']
        print(gname+' 走了个人！')
#以下为私聊检测
    async def on_direct_message_create(self, message: DirectMessage):
        talk = message.content
        str(talk)
        talk = talk.replace(f'<@!947704350086608309>','@'+str(self.robot.name))
        print(f'消息内容：'+str(talk)+' | 用户：'+str(message.author.username))
        _log.info(f'消息内容：'+str(talk)+' | 用户：'+str(message.author.username))
    #以下为/SC禁用物品，获取default_diffuse.png
        if "SC禁用物品" in message.content:
            try:
                await message.reply(content=f"SC已禁用的图片：", file_image="resource/badge/default_diffuse.png")
                _log.info(message.author.username)
            except Exception as e:
                await message.reply(content=f"发生错误:"+str(e))
    #以下为/帮助与/help，获取帮助列表
        elif "帮助"in message.content or "/help"in message.content:
            await message.reply(content=f"我是由LittleDuck__编写的机器人\n可点击我主页加我官方频道\n指令列表:\n/SC禁用物品————获取一张图片\n/帮助————打开此菜单\n/sc3d————格式：/sc3d 文件名（仅支持png)\n/image————格式：/image 文件名\n/udp————更新人数子频道\n/info————获取频道详情信息\n/cinfo————获取此子频道详情信息")
    #以下为/sc3d，获取sc3d文件夹内图片
        elif "sc3d" in message.content:
            if "spray_8bit" in message.content:
                await message.reply(content=f"以下是你需要的文件", file_image='resource/sc3d/spray_8bit.png')
            elif "spray" in message.content or "lightmap" in message.content or"trail" in message.content or "tex" in message.content or "ball" in message.content or "bone" in message.content or "brock" in message.content:
                try:
                    a = {message.content}
                    print(a)
                    a1 = re.sub('[ /{''}]','',str(a))
                    print(a1)
                    a1=a1.replace('<@!947704350086608309>','')
                    print(a1)
                    a1=a1.replace('sc3d','')
                    print(a1)
                    await message.reply(content=r"以下是你需要的文件", file_image='resource/sc3d/'+ eval(a1))
                except Exception as e:
                    await message.reply(content=f"发生错误:"+str(e))
                    print ("错误详细信息："+(traceback.format_exc()))
            else:
                await message.reply(content=f"找不到你要的文件喵，格式为：/sc3d 文件名（带后缀）")
    #以下为/image，获取image文件夹图片
        elif "image" in message.content:
            try:
                a = {message.content}
                print(a)
                a1 = re.sub('[ /{''}]','',str(a))
                print(a1)
                a1=a1.replace('<@!947704350086608309>','')
                print(a1)
                a1=a1.replace('image','')
                await message.reply(content=r"以下是你需要的文件", file_image='resource/image/'+ eval(a1))
            except Exception as e:
                await message.reply(content=f"发生错误！找不到你需要的文件，错误代码:"+str(e))
    #以下为/udp，更新人数子频道
        elif "udp" in message.content:
            try:
                guild = await self.api.get_guild(guild_id=message.guild_id)
                list(guild)
                mc = guild['member_count']
                print(mc)
                if message.guild_id == '14071334766867646580':
                    await self.api.update_channel(channel_id="12777219",name="频道人数："+str(mc))
                    await message.reply(content=f"已更新频道人数子频道："+str(mc))
                elif message.guild_id == '14183005142407712424':
                    await self.api.update_channel(channel_id="168792673",name="频道人数："+str(mc))
                    await message.reply(content=f"已更新频道人数子频道："+str(mc))
                else:
                    await message.reply(content=f"发生错误！该频道未开通此功能！此频道人数："+str(mc))
            except Exception as e:
                await message.reply(content=f"发生错误:"+str(e))
    #以下为/info，获取频道详情信息
        elif "info" in message.content:
            try:
                ginfo = await self.api.get_guild(guild_id=message.guild_id)
                gid = ginfo['id']
                gname = ginfo['name']
                gowner_id = ginfo['owner_id']
                gmember_count = ginfo['member_count']
                gmax_members = ginfo['max_members']
                gdescription = ginfo['description']
                if gdescription == "":
                    gdescription = "该频道没有描述！"
                    await message.reply(content=f"当前频道详情信息：\n频道ID："+str(gid)+"\n频道名称："+str(gname)+"\n频道主ID："+str(gowner_id)+"\n频道成员数："+str(gmember_count)+"\n频道最大成员数："+str(gmax_members)+"\n频道描述："+str(gdescription))
                else:
                    await message.reply(content=f"当前频道详情信息：\n频道ID："+str(gid)+"\n频道名称："+str(gname)+"\n频道主ID："+str(gowner_id)+"\n频道成员数："+str(gmember_count)+"\n频道最大成员数："+str(gmax_members)+"\n频道描述："+str(gdescription))
                print ("当前频道详情信息：\n频道ID："+str(gid)+"\n频道名称："+str(gname)+"\n频道主ID："+str(gowner_id)+"\n频道成员数："+str(gmember_count)+"\n频道最大成员数："+str(gmax_members)+"\n频道描述："+str(gdescription))
            except Exception as e:
                await message.reply(content=f"发生错误:"+str(e))
    #以下为/cinfo，获取子频道详情信息
        elif "cinfo" in message.content:
            try:
                cinfo = await self.api.get_channel(channel_id=message.channel_id)
                cid = cinfo['id']
                cname = cinfo['name']
                cguild_id = cinfo['guild_id']
                ctype = cinfo['type']
                csub_type = cinfo['sub_type']
                cposition = cinfo['position']
                cparent_id = cinfo['parent_id']
                cowner_id = cinfo['owner_id']
                print("当前子频道详情信息：\n子频道ID："+str(cid)+"\n子频道名称："+str(cname)+"\n所属频道ID："+str(cguild_id)+"\n子频道类型："+str(ctype)+"\n子频道子类型："+str(csub_type)+"\n子频道排序："+str(cposition)+"\n子频道分组ID："+str(cparent_id)+"\n子频道创建人ID："+str(cowner_id))
                await message.reply(content=f"当前子频道详情信息：\n子频道ID："+str(cid)+"\n子频道名称："+str(cname)+"\n所属频道ID："+str(cguild_id)+"\n子频道类型："+str(ctype)+"\n子频道子类型："+str(csub_type)+"\n子频道排序："+str(cposition)+"\n子频道分组ID："+str(cparent_id)+"\n子频道创建人ID："+str(cowner_id))
            except Exception as e:
                await message.reply(content=f"发生错误:"+str(e))
    #以下为服务器状态设置
        elif "<@!947704350086608309> g" == message.content or "<@!947704350086608309> y" == message.content or "<@!947704350086608309> r"== message.content:
            try:
                if "701266979954431539" == message.author.id or "11247367811761452321" == message.author.id:
                    if "r" in message.content:
                        await self.api.update_channel(channel_id="156024986",name="服务器状态：🔴")
                        await message.reply(content=f"已更新服务器状态子频道：🔴")
                    elif "y" in message.content:
                        await self.api.update_channel(channel_id="156024986",name="服务器状态：🟡")
                        await message.reply(content=f"已更新服务器状态子频道：🟡")
                    else:
                        await self.api.update_channel(channel_id="156024986",name="服务器状态：🟢")
                        await message.reply(content=f"已更新服务器状态子频道：🟢")
                else:
                    await message.reply(content=f"你没有权限执行此命令！")
            except Exception as e:
                await message.reply(content=f"发生错误:"+str(e))
        elif "test" in message.content:
            print(message.author.id)
            await message.reply(content=f"获取信息成功，用户ID："+str(message.author.id))
        #以下为未知命令处理       
        else:
            await message.reply(content=f"无效指令，请尝试/帮助!\nUnknown command \nPlease type /help.")
            print(message.content)

            
if __name__ == "__main__":
    # 通过预设置的类型，设置需要监听的事件通道
    # intents = botpy.Intents.none()
    # intents.public_guild_messages=True

    # 通过kwargs，设置需要监听的事件通道
    intents = botpy.Intents.all()
    client = MyClient(intents=intents)
    client.run(appid=config["appid"], token=config["token"])
