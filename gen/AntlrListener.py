# Generated from E:/new/antlrg/ScratchAnalysis\Antlr.g4 by ANTLR 4.7
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from antlr4 import *


# This class defines a complete listener for a parse tree produced by AntlrParser.
class AntlrListener(ParseTreeListener):
    def __init__(self):
        self.deadcode_flag = False
        self.max_depth = 0   # 语法树的最大深度
        self.max_if_depth = 0  # 最大if语句的深度
        self.max_until_depth = 0  # 最大until语句的深度
        self.max_repeat_depth = 0  # 最大repeat语句的深度
        self.if_count = 0  # if语句的数量
        self.until_count = 0  # until语句的数量
        self.repeat_count = 0  # repeat语句的数量
        self.scripts_count = 0  # 脚本语句scripts的数量
        self.comments_count = 0  # 代码评论的数目
        self.depth = 0  # 总深度
        self.if_depth = 0  # if语句的深度
        self.until_depth = 0  # until语句的深度
        self.repeat_depth = 0  # repeat语句的深度
        self.proj_count = 0  # 自定义函数proj的数目
        self.sprits_count = 0  # 角色sprits的数目
        self.wg_count = 0  # 小绿旗子的数目
        self.clone_count = 0  # clone语句的数目
        self.whenclick_count = 0  # 鼠标点击事件的数目
        self.whenkey_count = 0  # 键盘输入事件的数目
        self.whdrop_count = 0  # 背景切换的数目
        self.whreceive_count = 0  # 接收信号模块的数目
        self.whsensor_count = 0  # 输入音频视频的数目
        self.deadcode_count = 0  # 死代码块的数目
        self.missing_startup_count = 0  # 缺少启动语句block数目
        self.broadcastlist = []  # 广播发送的所有内容
        self.receivelist = []  # 广播接收的所有内容
        self.Meaningless_count = 0  # 无效命名数目
        self.initit = 0  # 是否初始化的标志
        self.attributeInitit = 0  # 角色属性初始化标志
        self.Recursively = 0  # 递归的数目
        self.SayandSound = 0  # 声画匹配的标志
        self.backgroud = 0  # 背景的数目
        self.sound_use = 0  # 使用音乐的次数
        self.instrument_use = 0  # 使用乐器的次数
        self.sprit_costume = 0  # 是否切换了造型
        # self.comments_count=0#是否切换了造型
        self.whenkey_countlist = []
        self.whenclick_countlist = []
        self.whenscene_countlist = []
        self.whenireceive_countlist = []
        self.whensensor_countlist = []

        self.motionnum = 0  # 动作类模块
        self.looklikenum = 0  # 外观类模块
        self.soundsnum = 0  # 声音类模块
        self.drawnum = 0  # 画笔类模块
        self.when_count = 0  # 事件类模块
        self.control_count = 0  # 控制类模块
        self.sensor_count = 0  # 测试类模块
        self.operate_count = 0  # 运算类模块
        self.more_count = 0  # 更多类模块
        self.data_count = 0  # 数据类模块

        self.ap_score = 0  # Abstraction and problem decomposition 得分
        self.Parallelism_score = 0  # Parallelism得分
        self.Synchronization = 0  # Synchronization得分
        self.FlowControl_score = 0  # FlowControl得分
        self.UserInteractivity = 0  # UserInteractivity得分
        self.LogicalThinking = 0  # LogicalThinking得分
        self.DataRepresentation = 1  # 因为太多了，默认先直接给1分.....
        self.CodeOrganization = 0  # 代码组织得分
        self.content = 0  # 作品内容得分

        self.score = {}
        self.hint = []
        self.Meaningless_list = []

        self.have_insert = False
        self.profile = {}

        self.isFirst = []
        self.first = []
        self.linkedList = []
        self.isQueue = []  # 判断是否存在队列
        self.isStack = []  # 判断是否存在栈

    def create_score(self):#评分标准
        self.score['Abstraction'] = self.ap_score  # 抽象和问题解决
        self.score['Parallelism'] = self.Parallelism_score  # 并行
        self.score['LogicalThinking'] = self.LogicalThinking  # 逻辑思维
        self.score['Synchronization'] = self.Synchronization  # 同步
        self.score['FlowControl'] = self.FlowControl_score  # 顺序控制
        self.score['UserInteractivity'] = self.UserInteractivity  # 用户交互
        self.score['DataRepresentation'] = self.DataRepresentation  # 数据表示
        self.score['CodeOrganization'] = self.CodeOrganization  # 代码组织
        self.score['Content'] = self.content  # 内容

    def create_profile(self):
        self.profile['motions'] = self.motionnum
        self.profile['looklike'] = self.looklikenum
        self.profile['sounds'] = self.soundsnum
        self.profile['draw'] = self.drawnum
        self.profile['event'] = self.when_count
        self.profile['control'] = self.control_count
        self.profile['sensor'] = self.sensor_count
        self.profile['operate'] = self.operate_count
        self.profile['more'] = self.more_count
        self.profile['data'] = self.data_count
        self.profile['backdrop'] = self.backgroud
        self.profile['sprites'] = self.sprits_count
        # self.profile['snduse'] = self.sound_use

    def print_all(self):
        # ---------------------------------------------------------------------
        # print("max_depth:", self.max_depth)
        # print("max_if_depth:", self.max_if_depth)
        # print("max_until_depth:", self.max_until_depth)
        # print("max_repeat_depth:", self.max_repeat_depth)
        # print("if_count:", self.if_count)
        # print("until_count:", self.until_count)
        # print("repeat_count:", self.repeat_count)
        # print("scripts_count:", self.scripts_count)
        # print("comments_count:", self.comments_count)
        # print("proj_count:", self.proj_count)
        # print("sprits_count:", self.sprits_count)
        # print("deadcode_count:", self.deadcode_count)
        # ---------------------------------------------------------------------
        self.create_score()
        self.create_profile()
        # print(self.score,self.profile)

    # Enter a parse tree produced by AntlrParser#json.
    def enterJson(self, ctx):
        pass

    # Exit a parse tree produced by AntlrParser#json.
    def exitJson(self, ctx):
        # 是否有不匹配的广播
        # if (self.whdrop_count >= 2 or self.whreceive_count >= 2 or self.whsensor_count >= 2) and self.Parallelism_score < 3:
        #     self.Parallelism_score = 3
        if len(self.receivelist) != len(self.broadcastlist):
            self.hint.append("广播不匹配")
            # print("广播不匹配")
        else:
            for r in self.receivelist:
                if self.broadcastlist.count(r) == 0:
                    # print("广播不匹配")
                    if "广播不匹配" not in self.hint:
                        self.hint.append("广播不匹配")
                    self.deadcode_count += 1
        # 是否有无意义的角色命名
        if self.Meaningless_count > 0:
            s = "有" + str(self.Meaningless_count) + "个角色存在无意义命名,分别是:"
            # print("有" + str(self.Meaningless_count) + "个角色存在无意义命名,分别是:"),
            for i in self.Meaningless_list:
                s += i
            self.hint.append(s)
        # 是否进行初始化
        if self.initit > 0:
            # print("可能未初始化")
            self.hint.append("可能未初始化")
        # # 是否使用了递归
        # if self.Recursively > 0:
        #     if self.LogicalThinking < 3:
        #         self.LogicalThinking = 3
        #     # print("使用了" + str(self.Recursively) + "次递归")
        #     self.hint.append("使用了" + str(self.Recursively) + "次递归")
        # 是否声画同步
        if self.SayandSound > 0:
            self.hint.append("声画不同步")
            # print("声画不同步")

        # print("ifdepth:",self.max_if_depth)
        # print("sprite:",self.sprits_count)
        # print("custumes:",self.backgroud)
        # print("sounds:",self.sound_use)
        # print("instrument:",self.instrument_use)
        # print("人物造型切换:",self.instrument_use)

        # 评分标准3-5
        # print("max_if_depth", self.max_if_depth)
        if self.max_if_depth > 1 and self.LogicalThinking < 5:
            self.LogicalThinking = 5
            # print('评分标准3-5')
        # print("isFirst", self.isFirst)
        # print("first", self.first)
        # print("linkedList", self.linkedList)
        # print("queue", self.isQueue)
        # print("stack", self.isStack)

        # 评分标准8-4
        if self.missing_startup_count == 0 and self.CodeOrganization < 4:
            self.CodeOrganization = 4
            # print("评分标准8-4")


        # 评分标准8-1
        if self.attributeInitit == 1 and self.CodeOrganization < 1:
            self.CodeOrganization = 1
            # print("评分标准8-1")

        isfind = 1
        for content in self.receivelist:
            if self.broadcastlist.count(content) == 0:
                isfind = 0
                break
        # 评分标准8-5
        if self.receivelist and self.broadcastlist:
            if isfind == 1 and self.CodeOrganization < 5:
                self.CodeOrganization = 5
                # print("评分标准8-5")
        self.print_all()

    # Enter a parse tree produced by AntlrParser#obj.
    def enterObj(self, ctx):
        pass

    # Exit a parse tree produced by AntlrParser#obj.
    def exitObj(self, ctx):
        pass

    # Enter a parse tree produced by AntlrParser#pair.
    def enterPair(self, ctx):
        # 判断有多少个角色和角色的命名判定
        ctx_STRING = ctx.STRING()
        ctx_comment = ctx.SCRIPTCOMMENTS()
        if ctx_STRING:
            ctx_STRING_Text = ctx_STRING.getText()
            if ctx_STRING_Text == '"objName"':
                if ctx.value().STRING().getText() != '"Stage"'and ctx.value().STRING().getText() != '"舞台"':
                    self.sprits_count += 1  # 角色数目+1
                    # 评分标准1-2
                    if self.sprits_count > 1 and self.ap_score < 2:
                        self.ap_score = 2
                        # print("抽象和问题分解 2分")
                #是否存在无意义命名
                if ctx.value().STRING().getText().find('Sprite') > 0 or ctx.value().STRING().getText().find('角色') > 0:
                    self.Meaningless_count += 1
                    self.Meaningless_list.append(ctx.value().STRING().getText().strip('"'))
            # 链表
            if ctx_STRING_Text == '"listName"':
                    name = ctx.children[2].getText()
                    if name in self.linkedList:
                        pass
                    else:
                        self.linkedList.append(name)
                        self.isFirst.append(name)
                        self.first.append(name)
        if ctx_comment:
            ctx_comment_Text = ctx_comment.getText()
            # 评分标准8-3
            if ctx_comment_Text == '"scriptComments"':
                if self.CodeOrganization < 3:
                    self.CodeOrganization = 3
                # print("评分标准8-3")

    # Exit a parse tree produced by AntlrParser#pair.
    def exitPair(self, ctx):
        pass

    # Enter a parse tree produced by AntlrParser#scripts_array.
    def enterScripts_array(self, ctx):
        flag1 = 0
        flag2 = 0
        str2 = ctx.getText()
        str3 = str2
        # 关于初始化的几个方面
        # 评分标准7-3
        if '"setVar:to:"' in str2:
            if self.DataRepresentation < 3:
                self.DataRepresentation = 3
                # print('评分标准7-3')
            self.initit = 1
        #关于显示隐藏的初始化
        if str2.find('"hide"') > 0:
            if str2.find('"show"') < 0:
                self.initit = 1
        #关于角色造型的初始化
        if str2.find('"nextCostume"') > 0:
            if str2.find('"lookLike:"') < 0:
                self.initit = 1
                self.attributeInitit = 1
        #关于角色大小的初始化
        if str2.find('"changeSizeBy:"') > 0:
            if str2.find('"setSizeTo:"') < 0:
                self.initit = 1
                self.attributeInitit = 1
        #关于背景变化的初始化
        if str2.find('"nextScene"') > 0:
            if str2.find('"startScene"') < 0:
                self.initit = 1
                self.attributeInitit = 1
        #关于角色方向的初始化
        if str2.find('"turnRight:"') > 0 or str2.find('"turnLeft:"') > 0 or str2.find('"pointTowards:"') > 0:
            if str2.find('"heading:"') < 0:
                self.initit = 1
                self.attributeInitit = 1
        #关于角色位置的初始化
        if str2.find('"forward:"') > 0 or str2.find('"gotoSpriteOrMouse:"') > 0 or str2.find(
                '"glideSecs:toX:y:elapsed:from:"') > 0:
            if str2.find('"gotoX:y:"') < 0:
                self.initit = 1
                self.attributeInitit = 1
        #关于x坐标的初始化
        if str2.find('"changeXposBy:"') > 0:
            if str2.find('"xpos:"') < 0 and str2.find('"gotoX:y:"') < 0:
                self.initit = 1
        # 关于y坐标的初始化
        if str2.find('"changeYposBy:"') > 0:
            if str2.find('"ypos:"') < 0 and str2.find('"gotoX:y:"') < 0:
                self.initit = 1
        # 处理音画同步，要求是画面必须出现在声音之前
        # while str2.find("laySound") > 0 and flag2 == 0:
        #     soundstr = str2[str2.find("laySound"):str2.find("laySound") + 40]
        #     sc = ctx.getText().find(soundstr)
        #     str1 = str2[str2.find("laySound"):]
        #     s1 = str2.find("laySound")
        #     str1 = str1[:str1.find(']')]
        #     str1 = str1.split(',')
        #     str1 = str1[1].strip('"')
        #     while str3.find("say") > 0 and flag2 == 0:
        #         saystr = str3[str3.find("say"):str3.find("say") + 40]
        #         sy = ctx.getText().find(saystr)
        #         str4 = str3[str3.find("say"):]
        #         s2 = str3.find("say")
        #         str4 = str4[:str4.find(']')]
        #         str4 = str4.split(',')
        #         str4 = str4[1].strip('"')
        #         if str4 == str1 and sc < sy:
        #             self.SayandSound += 1
        #             flag2 = 1
        #             break
        #         elif str4 == str1 and sc > sy:
        #             str3 = str3[s2:]
        #             flag1 = 1
        #             break
        #         else:
        #             str3 = str3[s2:]
        #     str2 = str2[s1:]
        #     if flag1 == 0:
        #         str3 = ctx.getText()
        # # 评分标准1-1
        #
        # # 有scripts就给1分
        # # if self.deadcode_flag == False:
        # #     if self.FlowControl_score < 1:
        # #         self.FlowControl_score = 1

    # Exit a parse tree produced by AntlrParser#scripts_array.
    def exitScripts_array(self, ctx):
        pass

    # Enter a parse tree produced by AntlrParser#array.
    def enterArray(self, ctx):
        pass

    # Exit a parse tree produced by AntlrParser#array.
    def exitArray(self, ctx):
        pass

    # Enter a parse tree produced by AntlrParser#blocks_array.
    def enterBlocks_array(self, ctx):
        #检测没有控制模块开始的代码块，认定为死代码
        # if ctx.getText().find("when") == -1:
        #     self.deadcode_count += 1
        #     self.deadcode_flag = True
        #     self.missing_startup_count += 1

        # 评分标准5-1
        if (ctx.getChildCount()-1)/2-1 > 1 and self.deadcode_flag == False:
            if self.FlowControl_score < 1:
                self.FlowControl_score = 1
        pass

    # Exit a parse tree produced by AntlrParser#blocks_array.
    def exitBlocks_array(self, ctx):
        self.deadcode_flag = False
        pass

    # Enter a parse tree produced by AntlrParser#value.
    def enterValue(self, ctx):
        ctx_Text = ctx.getText()
        # print("ctx_Text", ctx_Text)
        # 评分标准1-3
        if ctx_Text == '"procDef"':
            self.proj_count += 1
            if self.proj_count > 0 and self.ap_score < 3:
                self.ap_score = 3
                # print("抽象和问题分解 3分")
        # 评分标准1-4
        if (ctx_Text == '"whenCloned"' or ctx_Text == '"createCloneOf"' or ctx_Text == '"deleteClone"') and self.deadcode_flag == False:
            self.clone_count += 1
            if self.clone_count > 0 and self.ap_score < 4:
                self.ap_score = 4
                # print("抽象和问题分解 4分")

        if '"whenKeyPressed"' == ctx_Text and self.deadcode_flag == False:
            # self.whenkey_count = len(ctx.parentCtx.children)
            meaning = (ctx.parentCtx.parentCtx.parentCtx.getChildCount()-1)/2-1
            if meaning >= 1:
                whenkey_count1 = ctx.parentCtx.children[3].getText()
                if self.whenkey_countlist.count(whenkey_count1) > 0:
                    self.whenkey_count += 2

                else:
                    self.whenkey_countlist.append(whenkey_count1)
                # 评分标准6-2
                if self.UserInteractivity < 2:
                    self.UserInteractivity = 2
                # self.whenkey_count += 1
            # print(whenkey_count1)
            # 评分标准2-2
            if (self.whenkey_count >= 2 or self.whenclick_count >= 2) and self.Parallelism_score < 2:
                self.Parallelism_score = 2
                # print("并行 2分")
            # 评分标准4-2
            if self.Synchronization < 2:
                self.Synchronization = 2
                # print('评分标准4-2')

        if '"whenClicked"' == ctx_Text and self.deadcode_flag == False:
            whcl_meaning = (ctx.parentCtx.parentCtx.parentCtx.getChildCount() - 1) / 2 - 1
            # print(ctx.parentCtx.parentCtx.getChildCount())
            if whcl_meaning >= 1:
                # whenclick_name = ctx.parentCtx.parentCtx.parentCtx.parentCtx.parentCtx.parentCtx.children[1].children[
                #     2].getText()
                # if self.whenclick_countlist.count(whenclick_name) > 0:
                #     self.whenclick_count += 2
                # else:
                #     self.whenclick_countlist.append(whenclick_name)
                # 评分标准6-2
                if self.UserInteractivity < 2:
                    self.UserInteractivity = 2
            # 评分标准2-2
            if (self.whenkey_count >= 2 or self.whenclick_count >= 2) and self.Parallelism_score < 2:
                self.Parallelism_score = 2
                # print("并行 2分")
            # 评分标准4-2
            if self.Synchronization < 2:
                self.Synchronization = 2
                # print('评分标准4-2')

        if '"whenSceneStarts"' == ctx_Text and self.deadcode_flag == False:
            meaning = (ctx.parentCtx.parentCtx.parentCtx.getChildCount() - 1) / 2 - 1
            if meaning >= 1:
                whdrop_count1 = ctx.parentCtx.children[3].getText()
                if self.whenscene_countlist.count(whdrop_count1) > 0:
                    self.whdrop_count += 2
                else:
                    self.whenscene_countlist.append(whdrop_count1)
            # 评分标准2-3
            if self.whdrop_count >= 2 and self.Parallelism_score < 3:
                self.Parallelism_score = 3
                # print("并行 3分")
                # print('get2-3')
            # 评分标准4-4
            if self.Synchronization < 4:
                self.Synchronization = 4
                # print('评分标准4-4')
        if '"whenSensorGreaterThan"' == ctx_Text and self.deadcode_flag == False:
            meaning = (ctx.parentCtx.parentCtx.parentCtx.getChildCount() - 1) / 2 - 1
            if meaning >= 1:
                whsensor_count1 = ctx.parentCtx.children[3].getText()
                if self.whensensor_countlist.count(whsensor_count1) > 0:
                    self.whsensor_count += 2
                else:
                    self.whensensor_countlist.append(whsensor_count1)
            # 评分标准2-5
            if self.whsensor_count >= 2 and self.Parallelism_score < 5:
                self.Parallelism_score = 5
                # print("并行 5分")

        if '"doAsk"' == ctx_Text and self.deadcode_flag == False:
            self.sensor_count += 1
            # 评分标准6-3
            if self.UserInteractivity < 3:
                self.UserInteractivity = 3

        if '"setVideoState"' == ctx_Text and self.deadcode_flag == False:
            # 评分标准6-5
            if self.UserInteractivity < 3:
                self.UserInteractivity = 3

        if '"soundLevel"' == ctx_Text and self.deadcode_flag == False:
            # 评分标准6-4
            if self.UserInteractivity < 3:
                self.UserInteractivity = 3

        # logic_operator = ('"&"', '"|"', '"not"', '"<"', '">"', '"="')
        # if (ctx_Text in logic_operator) and (self.LogicalThinking < 3) and self.deadcode_flag == False:
        #     self.LogicalThinking = 3

        # 评分标准4-1
        if '"wait:elapsed:from:"' == ctx_Text and self.deadcode_flag == False:
            if self.Synchronization < 1:
                self.Synchronization = 1
                # print('评分标准4-1')
            if self.UserInteractivity < 2:
                self.UserInteractivity = 2
        # 评分标准4-3
        if '"stopScripts"' == ctx_Text and self.deadcode_flag == False:
            if self.Synchronization < 3:
                self.Synchronization = 3

        # sync_3p = ('"doBroadcastAndWait"', '"doWaitUntil"')
        # if ctx_Text in sync_3p and self.deadcode_flag == False:
        #     if self.Synchronization < 3:
        #         self.Synchronization = 3
        # if ctx_Text == '"whenSceneStarts"' and self.deadcode_flag == False:
        #     whSS = (ctx.parentCtx.parentCtx.parentCtx.getChildCount() - 1) / 2 - 1
        #     if whSS >= 1:
        #         if self.Synchronization < 3:
        #             self.Synchronization = 3
        #         whenscense_count = ctx.parentCtx.children[3].getText()
        #
        #         if self.whenscene_countlist.count(whenscense_count) > 0:
        #             self.whdrop_count += 2
        #         else:
        #             self.whenscene_countlist.append(whenscense_count)

        if ctx_Text == '"insert:at:ofList:"':
            self.have_insert = True

        if ctx_Text == '"deleteLine:ofList"':
            if self.ap_score < 3:
                self.ap_score = 3
        sounds = {'"playSound:"', '"doPlaySoundAndWait"', '"playDrum"', '"noteOn:duration:elapsed:from:"'}
        if ctx_Text in sounds and self.deadcode_flag == False:
            self.sound_use += 1

        sprit_cos = {'"lookLike:"', '"nextCostume"'}
        if ctx_Text in sprit_cos and self.deadcode_flag == False:
            self.sprit_costume += 1

        if ctx_Text == '"instrument:"' and self.deadcode_flag == False:
            self.instrument_use += 1

        motions={'"forward:"','"turnRight:"','"turnLeft:"','"heading:"','"pointTowards:"','"gotoX:y:"','"gotoSpriteOrMouse:"','"glideSecs:toX:y:elapsed:from:"','"changeXposBy:"','"xpos:"','"changeYposBy:"','"ypos:"','"bounceOffEdge"','"setRotationStyle"'}
        if ctx_Text in motions and self.deadcode_flag == False:
            self.motionnum += 1
            # print(ctx_Text)

        lookikes = {'"say:duration:elapsed:from:"', '"say:"', '"think:duration:elapsed:from:"', '"think:"', '"show"', '"hide"',
                   '"lookLike:"', '"nextCostume"', '"startScene"', '"changeGraphicEffect:by:"',
                   '"setGraphicEffect:to:"', '"filterReset"', '"changeSizeBy:"', '"setSizeTo:"','"comeToFront"','"goBackByLayers:"'}
        if ctx_Text in lookikes and self.deadcode_flag == False:
            self.looklikenum += 1

        soundss = {'"playSound:"', '"doPlaySoundAndWait"', '"stopAllSounds"', '"playDrum"', '"rest:elapsed:from:"',
                    '"noteOn:duration:elapsed:from:"',
                    '"instrument:"', '"changeVolumeBy:"', '"setVolumeTo:"', '"changeTempoBy:"',
                    '"setTempoTo:"'}
        if ctx_Text in soundss and self.deadcode_flag == False:
            self.soundsnum += 1

        drawlist = {'"clearPenTrails"', '"stampCostume"', '"putPenDown"', '"putPenUp"', '"penColor:"',
                   '"changePenHueBy:"',
                   '"setPenHueTo:"', '"changePenShadeBy:"', '"setPenShadeTo:"', '"changePenSizeBy:"',
                   '"penSize:"'}
        if ctx_Text in drawlist and self.deadcode_flag == False:
            self.drawnum += 1

        whenlist = {'"whenKeyPressed"', '"whenClicked"', '"whenSceneStarts"'}
        if ctx_Text in whenlist and self.deadcode_flag == False:
            self.when_count += 1
            # print(ctx_Text)

        controllist = {'"whenCloned"', '"wait:elapsed:from:"', '"stopScripts"', '"createCloneOf"', '"deleteClone"'}
        if ctx_Text in controllist and self.deadcode_flag == False:
            self.control_count += 1
            # print(ctx_Text)

        sensorlist = {'"keyPressed:"', '"mousePressed"', '"mouseX"', '"mouseY"', '"soundLevel"', '"senseVideoMotion"', '"setVideoState"', '"distanceTo:"','"color:sees:"','"touchingColor:"','"touching:"','"timer"','"getAttribute:of:"','"timeAndDate"','"timestamp"','"getUserName"'}
        if ctx_Text in sensorlist and self.deadcode_flag == False:
            self.sensor_count += 1
            # print(ctx_Text)

            # print(ctx_Text)

        operatelist = {'"+"', '"-"', '"*"', '"\/"', '"randomFrom:to:"', '"<"',
                       '"="', '">"', '"&"', '"|"', '"not"', '"concatenate:with:"',
                       '"letter:of:"', '"stringLength:"', '"%"', '"rounded"', '"computeFunction:of:"'}
        if ctx_Text in operatelist and self.deadcode_flag == False:
            self.operate_count += 1
            # print(ctx_Text)

        datalist = {'"readVariable"', '"setVar:to:"', '"changeVar:by:"', '"showVariable:"', '"hideVariable:"'}
        arraylist = {'"contentsOfList:"',
                       '"getLine:ofList:"', '"lineCountOfList:"', '"list:contains:"', '"showList:"', '"append:toList:"', '"append:toList:"',
                       '"deleteLine:ofList:"', '"insert:at:ofList:"', '"setLine:ofList:to:"', '"hideList:"'}
        if (ctx_Text in datalist or ctx_Text in arraylist) and self.deadcode_flag == False:
            self.data_count += 1

        if ctx_Text in datalist and self.deadcode_flag == False:
            # 评分标准7-2
            if self.DataRepresentation < 2:
                self.DataRepresentation = 2

        if ctx_Text in arraylist and self.deadcode_flag == False:
            # 评分标准7-4
            if self.DataRepresentation < 4:
                self.DataRepresentation = 4

        if ctx_Text == '"append:toList:"':
            name = ctx.parentCtx.children[5].getText()
            if name in self.isFirst:
                self.isQueue.append(name)
                self.isFirst.remove(name)
            if name in self.first:
                self.first.remove(name)
            if name in self.isStack:
                self.isStack.remove(name)

        if ctx_Text == '"deleteLine:ofList:"':
            loc = ctx.parentCtx.children[3].getText()
            name = ctx.parentCtx.children[5].getText()
            if loc == "1":
                if name in self.isFirst:
                    self.isQueue.append(name)
                    self.isFirst.remove(name)
            else:
                if name in self.isFirst:
                    self.isFirst.remove(name)
                if name in self.isQueue:
                    self.isQueue.remove(name)
            if loc == "1":
                if name in self.first:
                    self.isStack.append(name)
                    self.first.remove(name)
            else:
                if name in self.first:
                    self.first.remove(name)
                if name in self.isStack:
                    self.isStack.remove(name)
            # print("name=", name, "loc=", loc)

        if ctx_Text == '"insert:at:ofList:"':
            loc = ctx.parentCtx.children[5].getText()
            name = ctx.parentCtx.children[7].getText()
            if loc == '"last"':
                if name in self.isFirst:
                    self.isQueue.append(name)
                    self.isFirst.remove(name)
            else:
                if name in self.isFirst:
                    self.isFirst.remove(name)
                if name in self.isQueue:
                    self.isQueue.remove(name)
            if loc == "1":
                if name in self.first:
                    self.isStack.append(name)
                    self.first.remove(name)
            else:
                if name in self.first:
                    self.first.remove(name)
                if name in self.isStack:
                    self.isStack.remove(name)

        if ctx_Text == '"setLine:ofList:to:"':
            name = ctx.parentCtx.children[5].getText()
            if name in self.isFirst:
                self.isFirst.remove(name)
            if name in self.isQueue:
                self.isQueue.remove(name)
            if name in self.first:
                self.first.remove(name)
            if name in self.isStack:
                self.isStack.remove(name)

        # 评分标准9-1
        if ctx_Text == '"startScene"' or ctx_Text == '"startSceneAndWait"':
            if self.content < 1:
                self.content = 1
                # print("评分标准9-1")

        # 评分标准9-2
        if ctx_Text == '"lookLike:"' or ctx_Text == '"nextCostume"':
            if self.content < 2:
                self.content = 2
                # print("评分标准9-2")

        # 评分标准9-3
        if ctx_Text == '"touching:"' or ctx_Text == '"touchingColor:"' or ctx_Text == '"color:sees:"' or \
                        ctx_Text == '"keyPressed:"' or ctx_Text == '"mousePressed"':
            if self.content < 3:
                self.content = 3
                # print("评分标准9-3")

        # 评分标准9-4
        if ctx_Text == '"playSound:"' or ctx_Text == '"doPlaySoundAndWait"' or ctx_Text == '"playDrum"' or \
                        ctx_Text == '"noteOn:duration:elapsed:from:"':
            if self.content < 4:
                self.content = 4
                # print("评分标准9-4")

        # 评分标准9-5
        if ctx_Text == '"putPenDown"':
            if self.content < 5:
                self.content = 5
                # print("评分标准9-5")

    # Exit a parse tree produced by AntlrParser#value.
    def exitValue(self, ctx):
        pass

    # Enter a parse tree produced by AntlrParser#cblock_value.
    def enterCblock_value(self, ctx):
        if ctx.WHENGREENFLAG():
            wg_meaning = (ctx.parentCtx.getChildCount()-1)/2-1
            if wg_meaning >= 1:
                self.when_count += 1
                self.wg_count += 1
                # 评分标准6-1
                if self.UserInteractivity < 1:
                    self.UserInteractivity = 1
                    # print("评分标准6-1")
            # 评分标准2-1
            # self.wg_count = (len(ctx.parentCtx.children)-1)/2-1;

            # print(self.wg_count);
            if self.wg_count >= 2 and self.Parallelism_score == 0:
                self.Parallelism_score = 1
                # print("并行 1分")

        if self.deadcode_flag == False:
            self.scripts_count += 1
            # 评分标准1-1
            if self.scripts_count > 1 and self.ap_score == 0:
                self.ap_score = 1
                # print("抽象和问题分解 1分")
            # print(ctx.getText(), self.scripts_count)
            # print(self.scripts_count)

        if self.sprits_count > 1 and self.scripts_count > 1 and self.ap_score < 1:
            self.ap_score = 1

    # Exit a parse tree produced by AntlrParser#cblock_value.
    def exitCblock_value(self, ctx):
        # self.wg_count=0;
        pass

    # Enter a parse tree produced by AntlrParser#cblock_doRepeat.
    def enterCblock_doRepeat(self, ctx):
        if self.deadcode_flag == False:
            self.repeat_depth += 1
            if self.repeat_depth > self.max_repeat_depth:
                self.max_repeat_depth = self.repeat_depth
            # 评分标准5-2
            if self.FlowControl_score < 2:
                self.FlowControl_score = 2
            self.control_count += 1
        # print(ctx.getText())
        pass

    # Exit a parse tree produced by AntlrParser#cblock_doRepeat.
    def exitCblock_doRepeat(self, ctx):
        self.repeat_depth -= 1
        pass

    # Enter a parse tree produced by AntlrParser#cblock_doUntil.
    def enterCblock_doUntil(self, ctx):
        if self.deadcode_flag == False:
            self.until_depth += 1
            if self.until_depth > self.max_until_depth:
                self.max_until_depth = self.until_depth
            # 评分标准5-3
            if self.FlowControl_score < 3:
                self.FlowControl_score = 3
            self.control_count += 1
        # print(ctx.getText())
        pass

    # Exit a parse tree produced by AntlrParser#cblock_doUntil.
    def exitCblock_doUntil(self, ctx):
        self.until_depth -= 1
        pass

    # Enter a parse tree produced by AntlrParser#cblock_doIfElse.
    def enterCblock_doIfElse(self, ctx):
        if self.deadcode_flag == False:
            self.if_depth += 1
            if self.if_depth > self.max_if_depth:
                self.max_if_depth = self.if_depth
            # 评分标准3-2
            if self.LogicalThinking < 2:
                self.LogicalThinking = 2
                # print("评分标准3-2")
            self.control_count += 1
        pass

    # Exit a parse tree produced by AntlrParser#cblock_doIfElse.
    def exitCblock_doIfElse(self, ctx):
        self.if_depth -= 1
        pass

    # Enter a parse tree produced by AntlrParser#cblock_doIF.
    # 将if中比较静态的两部分进行比较,得到某部分是不是死代码
    def enterCblock_doIF(self, ctx):
        if self.deadcode_flag == False:
            self.if_depth += 1

            if self.if_depth > self.max_if_depth:
                self.max_if_depth = self.if_depth
            # 评分标准3-1
            if self.LogicalThinking < 1:
                self.LogicalThinking = 1
                # print("逻辑思维 1分")

            self.control_count += 1
        pass

    # Exit a parse tree produced by AntlrParser#cblock_doIF.
    def exitCblock_doIF(self, ctx):
        self.if_depth -= 1
        pass

    # Enter a parse tree produced by AntlrParser#cblock_doWaitUntil.
    def enterCblock_doWaitUntil(self, ctx):
        if self.deadcode_flag == False:
            # if self.Synchronization < 3:
            #     self.Synchronization = 3
            self.control_count += 1
            # 评分标准4-5
            if self.Synchronization < 5:
                self.Synchronization = 5
                # print('评分标准4-5')
        # print(ctx.getText())

    # Exit a parse tree produced by AntlrParser#cblock_doWaitUntil.
    def exitCblock_doWaitUntil(self, ctx):
        pass

    # Enter a parse tree produced by AntlrParser#cblock_doForever.
    def enterCblock_doForever(self, ctx):
        if self.deadcode_flag == False:
            # 评分标准5-2
            if self.FlowControl_score < 2:
                self.FlowControl_score = 2
            self.control_count += 1
        # print(ctx.getText())
        pass

    # Exit a parse tree produced by AntlrParser#cblock_doForever.
    def exitCblock_doForever(self, ctx):
        pass

    # Enter a parse tree produced by AntlrParser#cblock_doBroadcast.
    # 发送广播模块发送的内容
    def enterCblock_doBroadcast(self, ctx):
        if self.deadcode_flag == False:
            self.when_count += 1

            ctxText = ctx.getText()
            # print("enterCblock_doBroadcast", ctxText)
            str1 = ctxText.split(",")
            str1 = str1[1][:-2]
            broadcastcontent = str1.strip('"')
        # print(broadcastcontent)
        # # 判断是否发送过该该内容
            if broadcastcontent.find("readVariable") < 0 and self.broadcastlist.count(broadcastcontent) == 0:
                self.broadcastlist.append(broadcastcontent)
            # 评分标准4-4
            if '"doBroadcastAndWait"' in ctxText:
                if self.Synchronization < 4:
                    self.Synchronization = 4
            # 评分标准4-3
            if '"broadcast"' in ctxText:
                if self.Synchronization < 3:
                    self.Synchronization = 3
                    # print('评分标准4-3')
        pass

    # Exit a parse tree produced by AntlrParser#cblock_doBroadcast.
    def exitCblock_doBroadcast(self, ctx):
        pass

    # Enter a parse tree produced by AntlrParser#cblock_whenIReceive.
    # 得到接收广播得到的内容
    def enterCblock_whenIReceive(self, ctx):
        self.when_count += 1
        ctxText = ctx.getText()
        str1 = ctxText.split(",")
        str1 = str1[1][:-2]
        receivecontent = str1.strip('"')
        # print(receivecontent)
        # print(self.receivelist.count(receivecontent))
        # 判断是是否已经收到过该内容
        if self.receivelist.count(receivecontent) == 0:
            self.receivelist.append(receivecontent)
        else:
            self.whreceive_count += 2

        ctx_Text = ctx.children[1].getText()
        if '"whenIReceive"' == ctx_Text:
            whreceive_count1 = ctx.children[3].getText()
            if self.whenscene_countlist.count(whreceive_count1) > 0:
                self.whreceive_count += 2
            else:
                self.whenscene_countlist.append(whreceive_count1)
            # 评分标准2-4
            if self.whreceive_count >= 2 and self.Parallelism_score < 4:
                self.Parallelism_score = 4
                # print("并行 4分")


    # Exit a parse tree produced by AntlrParser#cblock_whenIReceive.
    def exitCblock_whenIReceive(self, ctx):
        pass

    # Enter a parse tree produced by AntlrParser#procDef.
    # 判断是否含有递归存在
    def enterProcDef(self, ctx):
        self.proj_count += 1
        self.more_count += 1
        # 评分标准1-3
        if self.proj_count > 0 and self.ap_score < 3:
            self.ap_score = 3

        ctxText = ctx.getText()
        ctxValue = ctx.value()
        if ctxValue:
            procname=ctxValue[0].getText().strip('"')
            # print('procname', procname)
            if ctxText.find('"call"') > 0:
                self.more_count += 1
                str1 = ctxText[ctxText.find('"call"'):]
                # 评分标准1-5
                if str1.find(procname) > 0:
                    self.Recursively += 1
                    if self.LogicalThinking < 5:
                        self.LogicalThinking = 5
                        # print("抽象和问题分解 5分")
        pass

    # Exit a parse tree produced by AntlrParser#procDef.
    def exitProcDef(self, ctx):
        pass

    # Enter a parse tree produced by AntlrParser#comments_array.
    def enterComments_array(self, ctx):
        self.comments_count+=1
        pass

    # Exit a parse tree produced by AntlrParser#comments_array.
    def exitComments_array(self, ctx):
        pass

    # Enter a parse tree produced by AntlrParser#changename.
    def enterChangename(self, ctx):
        # 评分标准8-2
        if self.DataRepresentation < 2:
            self.DataRepresentation = 2
            # print("评分标准8-2")

    # Exit a parse tree produced by AntlrParser#changename.
    def exitChangename(self, ctx):
        pass

    # Enter a parse tree produced by AntlrParser#costumes.
    def enterCostumes(self, ctx):
        pass

    # Exit a parse tree produced by AntlrParser#costumes.
    def exitCostumes(self, ctx):
        pass

    # Enter a parse tree produced by AntlrParser#costume_content.
    def enterCostume_content(self, ctx):
        if ctx.parentCtx.parentCtx.parentCtx.getText().find('"Stage"')>0 or ctx.parentCtx.parentCtx.parentCtx.getText().find('"舞台"')>0:
            self.backgroud += 1
        pass

    # Exit a parse tree produced by AntlrParser#costume_content.
    def exitCostume_content(self, ctx):
        pass

    # Enter a parse tree produced by AntlrParser#condition.
    def enterCondition(self, ctx):
        ctx_Text = ctx.getText()
        # 评分标准3-4
        if 'doIf' in ctx.parentCtx.getText() and self.LogicalThinking < 4:
            if '&' in ctx_Text or '|' in ctx_Text or 'not' in ctx_Text:
                self.LogicalThinking = 4
                # print('评分标准3-4')
        # 评分标准3-3
        if 'doIfElse' in ctx.parentCtx.getText() and self.LogicalThinking < 3:
            if '+' in ctx_Text or '-' in ctx_Text or '*' in ctx_Text or '\/' in ctx_Text:
                self.LogicalThinking = 3
                # print('评分标准3-3')
        # 评分标准5-4
        if 'doUntil' in ctx.parentCtx.getText() and self.FlowControl_score < 4:
            if '&' in ctx_Text or '|' in ctx_Text or 'not' in ctx_Text:
                self.FlowControl_score = 4
                # print('评分标准5-4')
    # Exit a parse tree produced by AntlrParser#condition.
    def exitCondition(self, ctx):
        pass

    # Enter a parse tree produced by AntlrParser#content.
    def enterContent(self, ctx):
        ctx_Text = ctx.getText()
        # 评分标准5-5
        if self.FlowControl_score < 5:
            if 'doIf' in ctx_Text or 'doIfElse' in ctx_Text:
                self.FlowControl_score = 5
                # print('评分标准5-5')

    # Exit a parse tree produced by AntlrParser#content.
    def exitContent(self, ctx):
        pass