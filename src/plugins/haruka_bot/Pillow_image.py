# coding:utf-8
from PIL import Image, ImageDraw, ImageFont
from PIL import ImageGrab
import rsa,asyncio,json,os,math,requests,re
class image_hp():
    def __init__(self,message):
        self.hedaimage = message['face']
        self.uname = message['uname']
        self.type_message = message['type_message']
        self.message = message['message']
        # 信息头高度
        self.info_hight = 200

        if 'topic' in message:
            topics = []
            for topic in message['topic']:
                topics.append(f"#{topic}#")
            self.topic = topics
        else:
            self.topic = None
        
        if 'emoji' in message:
            emojis = {}
            for emoji in message['emoji']:
                emojis[str(emoji['text'])] = str(emoji['url'])
            self.emoji = emojis

        else:
            self.emoji = None
        
    def dynamic_style_translate(self): 
        """
        :说明:

          文本解析，把文本中的特殊元素分离并添加样式

        :返回:
            list[
                dict{
                    'message': message
                    'style': topic/emoji/normal/..
                    'url': emoji限定
                }
            ]
        """
        relist = []
        if self.topic:
            # 有topic
            count = 0
            for topic in self.topic:
                if count == 0:
                    # 拼接topic表达式
                    retopic = f"{topic}"
                else:
                    retopic = retopic + "|" +f"{topic}"
                count = count + 1
            relist.append(retopic)
        if self.emoji:
            # 有emoji
            count = 0
            for emoji in self.emoji:
                co = len(emoji)
                listl = list(emoji)
                # 处理[]
                listl.insert(len(emoji)-1,"\\")
                if count == 0:
                    # 拼接表达式
                    reemoji = f"\\{''.join(listl)}"
                else:
                    reemoji = reemoji + "|" +f"\\{''.join(listl)}"
                count = count + 1
            # 整合一些
            relist.append(reemoji)
        if self.emoji or self.topic:
            if len(relist) != 1:
                # 拼接总表达式
                restr = f"({relist[0]}|{relist[1]})"
            else:
                restr = f"({relist[0]})"
            mess = re.split(restr,self.message)
            mess = [x for x in mess if len(x)!=0]
            dg = []
            # 
            for msglist in mess:
                msgdict ={}
                if msglist in self.topic and self.topic:
                    msgdict['message'] = msglist
                    msgdict['style'] = "topic"
                    dg.append(msgdict)
                elif msglist in self.emoji and self.emoji:
                    msgdict['message'] = msglist
                    msgdict['style'] = "emoji"
                    msgdict['url'] = self.emoji[msglist]
                    dg.append(msgdict)
                else:
                    msgdict['message'] = msglist
                    msgdict['style'] = "normal"
                    dg.append(msgdict)
            return dg
        else:
            return None
            



    def image_rendering(self):
        """
        :说明:

          匹配类型，渲染图片

        :返回:
            图片
        """
        # 首先定义单位，用字符高度 中文汉字 1 数字英文符号0.5 表情1.5
        # 一行的上限是 25 个字符宽度
        # rendering。。。
        image = Image.new('RGBA',(1040,1000),'white')
        SZ = ImageFont.truetype('./syht/fount.ttf',40 )
        draw = ImageDraw.Draw(image)
        dynamic = self.dynamic_style_translate()
        rendering_bs = 0
        fount_sz = 40
        mx_line = 25
        # 换行
        len_hight = 30
        # 起始标记
        l = 1
        count = 40
        hight = 60
        for item in dynamic:
            # 字符计数
            # 渲染字
            if item['style'] == "normal" or item['style'] == "topic":
                text = list(item['message'])
                if item['style'] == "normal":
                    tfill=(0,0,0)
                else:
                    tfill=(31,134,193)
                for text_bit in text:
                    print(text_bit)
                    if text_bit == "#":
                        if count + 25 > 40*25:
                            hight = hight + 40 + 30
                            count = 40
                        draw.text((count, hight), text_bit, fill=tfill, font=SZ, embedded_color = True)
                        count = count + 25
                    else:
                        if count + 40 > 40*25:
                            hight = hight + 40 + 30
                            count = 40
                        draw.text((count, hight), text_bit, fill=tfill, font=SZ, embedded_color = True)
                        count = count + 40
                    if count > 40*25:
                        if count + 40 > 40*25:
                            hight = hight + 40 + 30
                            count = 40
                        hight = hight + 40 + 30
                        count = 40
            # 表情包
            elif item['style'] == "emoji":
                url = item['url']
                emojiimg = Image.open(requests.get(url, stream=True).raw).convert('RGBA')
                # 重设大小
                emojiimg = emojiimg.resize((60, 60), Image.ANTIALIAS)
                r,g,b,a = emojiimg.split()
                # 贴头像
                if count + 60 > 40*25:
                    hight = hight + 40 + 30
                    count = 40
                image.paste(emojiimg,(count,hight-10),mask = a)
                count = count + 60
                if count > 40*25:
                    hight = hight + 40 + 30
                    count = 40
            print(count)

        image.save("./image_save_20200509.png")


d = image_hp({"emoji":[{"text":"[热词系列_知识增加]","url": "https://i0.hdslb.com/bfs/emote/7496ff01fbac5304aa807732f1531d5986a0dfc3.png"}],"topic":["很多情况","有时候","标签","困难","精确","快速"],"face":"https://i1.hdslb.com/bfs/face/ac7b6d886b12434e885821703c93bed0a639fbc2.jpg","uname":"夏姬八彻","type_message":"新动态","message":"#很多情况#下@[热词系列_知识增加]人#有时候#会加很多莫名#标签#[热词系列_知识增加]在这种情况就很#困难#的去处理，所以我们要#精确##快速#的找到这些东西。#很多情况#下@[热词系列_知识增加]很多人#有时候#会加很多莫名#标签#[热词系列_知识增加]在这种情况就很#困难#的去处理，所以我们要#精确##快速#的找到这些东西。#很多情况#下@[热词系列_知识增加]很多人#有时候#会加很多莫名#标签#[热词系列_知识增加]在这种情况就很#困难#的去处理，所以我们要#精确##快速#的找到这些东西。#很多情况#下@[热词系列_知识增加]很多人#有时候#会加很多莫名#标签#[热词系列_知识增加]在这种情况就很#困难#的去处理，所以我们要#精确##快速#的找到这些东西。"})
print(d.dynamic_style_translate())
d.image_rendering()





                


        # msg_list = self.message.split('\n')  # 分割字符串成列表
        # new_msg_list = []
        # for tmsg_list in msg_list:
        #     message = re.sub("(.{25})", "\\1\n", tmsg_list, 0, re.DOTALL)
        #     msg_cut = message.split('\n')
        #     for msg in msg_cut:
        #         new_msg_list.append(msg)
        #     new_msg_list = new_msg_list
        
        # msg_list = new_msg_list

        # spaceNum = 30 # 行间距 设置(为8px
        # w = len(msg_list)*70
        # size = (1080,int(self.info_hight + w))
        # # 画布 以后再说
        # image = Image.new('RGBA',size,'white')
        # # 模板
        # # image = Image.open("./modle.jpg","r")
        # # 剪裁头像
        # # hdimg = Image.open(requests.get(self.hedaimage, stream=True).raw).convert('RGBA')
        # hdimg = Image.open("./fc.jpg","r")
        # w, h = hdimg.size
        # alpha_layer = Image.new('L', (w, w), 0)
        # draw = ImageDraw.Draw(alpha_layer)
        # draw.ellipse((0, 0, w, w), fill=255)
        # hdimg.putalpha(alpha_layer)
        # # 重设大小
        # hdimg = hdimg.resize((120, 120), Image.ANTIALIAS)
        # hdimg.save("./20200509.png")
        # r,g,b,a = hdimg.split()
        # # 贴头像
        # image.paste(hdimg,(35,50),mask = a)
        # # 字体
        # SBold = ImageFont.truetype('./syht/SourceHanSans-Bold.otf', 40)
        # SRegular = ImageFont.truetype('./syht/SourceHanSans-Regular.otf', 30)
        # STag = ImageFont.truetype('./syht/SourceHanSans-Bold.otf',40 )
        # SZ = ImageFont.truetype('./syht/fount.ttf',40 )
        # # 信息
        # draw = ImageDraw.Draw(image)
        # draw.text((170, 60),f"{self.uname}",fill=(225,112,160), font=SBold)
        # draw.text((170, 120),f"刚刚  · {self.type_message}",fill=(153,153,153), font=SRegular)
        # # 内容
        # # draw.text((40, 200),"#这是标签#",fill=(31,134,193), font=SZ)
        # h = ( 40 + spaceNum)  * len(msg_list)
        # for i in range(len(msg_list)):
        #     draw.text((40, 200 + i*( 40 + spaceNum)  ), msg_list[i], fill=(0,0,0), font=SZ, embedded_color = True) 
        # #draw.text((40, 200),f"{self.message}",fill=(0,0,0), font=SZ)