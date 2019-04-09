import codecs
import zipfile
import sys
import json



def unzip_scratch(filename):
    """
    unzip scratch project and extract project.json file
    :param filename: filename fo scratch project
    :return: null or project.json content
    """
    zfile = zipfile.ZipFile(filename, 'r')
    if "project.json" in zfile.namelist():
        data = zfile.read("project.json")
        data = data.decode()
        return data
    else:
        return None

def sort_blocks(name):
    """
    返回各类block数目
    :return:0~8:Motion,Events,Looks,Control,Sound,Sensing,Pen,Operatprs,More Data and Blocks
    """
    datalist = {'op_readVariable', 'op_setVar:to:', 'op_changeVar:by:', 'op_showVariable:', 'op_hideVariable:',
                'op_contentsOfList:',
                'op_getLine:ofList:', 'op_lineCountOfList:', 'op_list:contains:', 'op_showList:', 'op_append:toList:',
                'op_append:toList:',
                'op_deleteLine:ofList:', 'op_insert:at:ofList:', 'op_setLine:ofList:to:', 'op_hideList:','readVariable', 'setVar:to:', 'changeVar:by:', 'showVariable:', 'hideVariable:',
                'contentsOfList:',
                'getLine:ofList:', 'lineCountOfList:', 'list:contains:', 'showList:', 'append:toList:',
                'append:toList:',
                'deleteLine:ofList:', 'insert:at:ofList:', 'setLine:ofList:to:', 'hideList:'}
    if name in datalist:
        return 9

    elif name == 'op_forward:' or name == 'op_turnRight:' or name == 'op_turnLeft:' or name == 'op_heading:' \
            or name == 'op_pointTowards:' or name == 'op_gotoX:y:' or name == 'op_gotoSpriteOrMouse:' \
            or name == 'op_glideSecs:toX:y:elapsed:from:' or name == 'op_changeXposBy:' or name == 'op_xpos:' \
            or name == 'op_changeYposBy:' or name == 'op_ypos:' or name == 'op_bounceOffEdge' or name == 'op_setRotationStyle' \
            or name == 'op_xpos' or name == 'op_ypos' or name == 'op_heading' or name == 'forward:' or name == 'turnRight:' or name == 'turnLeft:' or name == 'heading:' \
            or name == 'pointTowards:' or name == 'gotoX:y:' or name == 'gotoSpriteOrMouse:' \
            or name == 'glideSecs:toX:y:elapsed:from:' or name == 'changeXposBy:' or name == 'xpos:' \
            or name == 'changeYposBy:' or name == 'ypos:' or name == 'bounceOffEdge' or name == 'setRotationStyle' \
            or name == 'xpos' or name == 'ypos' or name == 'heading':
        return 0

    elif name == 'op_whenGreenFlag' or name == 'op_whenKeyPressed' or name == 'op_whenClicked' or name == 'op_whenSceneStarts' \
            or name == 'op_whenSensorGreaterThan' or name == 'op_whenIReceive' or name == 'op_broadcast:' \
            or name == 'op_doBroadcastAndWait' or name == 'whenGreenFlag' or name == 'whenKeyPressed' or name == 'whenClicked' or name == 'whenSceneStarts' \
            or name == 'whenSensorGreaterThan' or name == 'whenIReceive' or name == 'broadcast:' \
            or name == 'doBroadcastAndWait':
        return 1

    elif name == 'op_say:duration:elapsed:from:' or name == 'op_say:' or name == 'op_think:duration:elapsed:from:' \
            or name == 'op_think:' or name == 'op_show' or name == 'op_hide' or name == 'op_lookLike:' \
            or name == 'op_nextCostume' or name == 'op_startScene' or name == 'op_changeGraphicEffect:by:' \
            or name == 'op_setGraphicEffect:to:' or name == 'filterReset' or name == 'changeSizeBy:' \
            or name == 'op_setSizeTo:' or name == 'op_comeToFront' or name == 'op_goBackByLayers:' \
            or name == 'op_costumeIndex' or name == 'op_sceneName' or name == 'op_scale' or name == 'say:duration:elapsed:from:' or name == 'say:' or name == 'think:duration:elapsed:from:' \
            or name == 'think:' or name == 'show' or name == 'hide' or name == 'lookLike:' \
            or name == 'nextCostume' or name == 'startScene' or name == 'changeGraphicEffect:by:' \
            or name == 'setGraphicEffect:to:' or name == 'filterReset' or name == 'changeSizeBy:' \
            or name == 'setSizeTo:' or name == 'comeToFront' or name == 'goBackByLayers:' \
            or name == 'costumeIndex' or name == 'sceneName' or name == 'scale':
        return 2

    elif name == 'op_wait:elapsed:from:' or name == 'op_doRepeat' or name == 'op_doForever' or name == 'op_doIf' \
            or name == 'op_doIfElse' or name == 'op_doWaitUntil' or name == 'op_doUntil' \
            or name == 'op_stopScripts' or name == 'op_whenCloned' or name == 'op_createCloneOf' \
            or name == 'op_deleteClone' or name == 'wait:elapsed:from:' or name == 'doRepeat' or name == 'doForever' or name == 'doIf' \
            or name == 'doIfElse' or name == 'doWaitUntil' or name == 'doUntil' \
            or name == 'stopScripts' or name == 'whenCloned' or name == 'createCloneOf' \
            or name == 'deleteClone':
        return 3

    elif name == 'op_playSound:' or name == 'op_doPlaySoundAndWait' or name == 'op_stopAllSounds' or name == 'op_playDrum' \
            or name == 'op_rest:elapsed:from:' or name == 'op_noteOn:duration:elapsed:from:' or name == 'op_instrument:' \
            or name == 'op_changeVolumeBy:' or name == 'op_setVolumeTo:' or name == 'op_volume' \
            or name == 'op_changeTempoBy:' or name == 'op_setTempoTo:' or name == 'op_tempo' or name == 'playSound:' or name == 'doPlaySoundAndWait' or name == 'stopAllSounds' or name == 'playDrum' \
            or name == 'rest:elapsed:from:' or name == 'noteOn:duration:elapsed:from:' or name == 'instrument:' \
            or name == 'changeVolumeBy:' or name == 'setVolumeTo:' or name == 'volume' \
            or name == 'changeTempoBy:' or name == 'setTempoTo:' or name == 'tempo':
        return 4

    elif name == 'op_touching:' or name == 'op_touchingColor:' or name == 'op_color:sees:' \
            or name == 'op_distanceTo:' or name == 'op_doAsk' or name == 'op_answer' or name == 'op_keyPressed:' \
            or name == 'op_mousePressed' or name == 'op_mouseX' or name == 'op_mouseY' \
            or name == 'op_soundLevel' or name == 'op_senseVideoMotion' or name == 'op_setVideoState' \
            or name == 'op_setVideoTransparency' or name == 'op_timer' or name == 'op_timerReset' \
            or name == 'op_getAttribute:of:' or name == 'op_timeAndDate' or name == 'op_timestamp' or name == 'op_getUserName' or name == 'touching:' or name == 'touchingColor:' or name == 'color:sees:' \
            or name == 'distanceTo:' or name == 'doAsk' or name == 'answer' or name == 'keyPressed:' \
            or name == 'mousePressed' or name == 'mouseX' or name == 'mouseY' \
            or name == 'soundLevel' or name == 'senseVideoMotion' or name == 'setVideoState' \
            or name == 'setVideoTransparency' or name == 'timer' or name == 'timerReset' \
            or name == 'getAttribute:of:' or name == 'timeAndDate' or name == 'timestamp' or name == 'getUserName':
        return 5

    elif name == 'op_clearPenTrails' or name == 'op_stampCostume' or name == 'op_putPenDown' or name == 'op_putPenUp' \
            or name == 'op_penColor:' or name == 'op_changePenHueBy:' or name == 'op_setPenHueTo:' \
            or name == 'op_changePenShadeBy:' or name == 'op_setPenShadeTo:' or name == 'op_changePenSizeBy:' \
            or name == 'op_penSize:' or name == 'clearPenTrails' or name == 'stampCostume' or name == 'putPenDown' or name == 'putPenUp' \
            or name == 'penColor:' or name == 'changePenHueBy:' or name == 'setPenHueTo:' \
            or name == 'changePenShadeBy:' or name == 'setPenShadeTo:' or name == 'changePenSizeBy:' \
            or name == 'penSize:':
        return 6

    elif name == 'op_+' or name == 'op_-' or name == 'op_*' or name == 'op_\/' \
            or name == 'op_randomFrom:to:' or name == 'op_<' or name == 'op_=' \
            or name == 'op_>' or name == 'op_&' or name == 'op_|' \
            or name == 'op_not' or name == 'op_concatenate:with:' or name == 'op_letter:of:' or name == 'op_stringLength:' \
            or name == 'op_%' or name == 'op_rounded' or name == 'op_computeFunction:of:'or name == '+' or name == '-' or name == '*' or name == '\/' \
            or name == 'randomFrom:to:' or name == '<' or name == '=' \
            or name == '>' or name == '&' or name == '|' \
            or name == 'not' or name == 'concatenate:with:' or name == 'letter:of:' or name == 'stringLength:' \
            or name == '%' or name == 'rounded' or name == 'computeFunction:of:':
        return 7

    else:
        return 8



def getModule(argv):
    # info = unzip_scratch('C:/Users/hrd/Desktop/a.zip')

    raw_json = unzip_scratch(argv)
    # encoded_json = codecs.decode(raw_json, 'utf-8', 'strict')
    dictaddblocknum={'Motion':0,'Events':0,'Looks':0,'Control':0,'Sound':0,'More':0,'Sensing':0,'Pen':0,'Operatprs':0,'data':0}
    dictdelblocknum={'Motion':0,'Events':0,'Looks':0,'Control':0,'Sound':0,'More':0,'Sensing':0,'Pen':0,'Operatprs':0,'data':0}
    dictdoublocknum={'Motion':0,'Events':0,'Looks':0,'Control':0,'Sound':0,'More':0,'Sensing':0,'Pen':0,'Operatprs':0,'data':0}
    dictdelcosnum={'dup':0,'del':0}
    dictdelbacnum={'dup':0,'del':0}
    dictdelsprnum={'dup':0,'del':0}
    dictdelsndnum={'dup':0,'del':0}
    dictaddcosnum={'add':0,'paint':0,'computer':0,'lib':0,'photo':0}
    dictaddsndnum={'add':0,'create':0,'computer':0,'lib':0}
    dictaddsprnum={'add':0,'paint':0,'computer':0,'lib':0,'photo':0}
    dictaddbacnum={'add':0,'paint':0,'computer':0,'lib':0,'photo':0}

    changecosname=0
    js= json.loads(raw_json)
    # print(js)
    if not js:
        return

    if 'doubleclick' in js:
        doublocknum = js['doubleclick']
        if dictdoublocknum:
            for i in doublocknum:
                # print(i[2])
                if i:
                    if sort_blocks(i[3]) == 0:
                        dictdoublocknum['Motion'] += 1
                    if sort_blocks(i[3]) == 1:
                        dictdoublocknum['Events'] += 1
                    if sort_blocks(i[3]) == 2:
                        dictdoublocknum['Looks'] += 1
                    if sort_blocks(i[3]) == 3:
                        dictdoublocknum['Control'] += 1
                    # if sort_blocks(i[3]) == 4:
                    #     dictdelblocknum['Sound'] += 1
                    if sort_blocks(i[3]) == 5:
                        print(dictdoublocknum['Sensing'])
                        dictdoublocknum['Sensing'] += 1
                    if sort_blocks(i[3]) == 6:
                        dictdoublocknum['Pen'] += 1
                    if sort_blocks(i[3]) == 7:
                        dictdoublocknum['Operatprs'] += 1
                    # if sort_blocks(i[3]) == 8:
                    #     dictdelblocknum['More'] += 1
                    if sort_blocks(i[3]) == 9:
                        dictdoublocknum['data'] += 1

    if 'addblockrec' in js:
        addblockrec = js['addblockrec']
        if addblockrec:
            for i in addblockrec:
                if i:
                # print(i[3])
                    if sort_blocks(i[3]) == 0:
                        dictaddblocknum['Motion'] += 1
                    if sort_blocks(i[3]) == 1:
                        dictaddblocknum['Events'] += 1
                    if sort_blocks(i[3]) == 2:
                        dictaddblocknum['Looks'] += 1
                    if sort_blocks(i[3]) == 3:
                        dictaddblocknum['Control'] += 1
                    # if sort_blocks(i[3]) == 4:
                    #     dictaddblocknum['Sound'] += 1
                    if sort_blocks(i[3]) == 5:
                        dictaddblocknum['Sensing'] += 1
                    if sort_blocks(i[3]) == 6:
                        dictaddblocknum['Pen'] += 1
                    if sort_blocks(i[3]) == 7:
                        dictaddblocknum['Operatprs'] += 1
                    # if sort_blocks(i[3]) == 8:
                    #     dictaddblocknum['More'] += 1
                    if sort_blocks(i[3]) == 9:
                        dictaddblocknum['data'] += 1

    if 'delblockrec' in js:
        delblockrec = js['delblockrec']
        if delblockrec:
            for i in delblockrec:
                # print(i[2])
                if i:
                    if sort_blocks(i[2]) == 0:
                        dictdelblocknum['Motion'] += 1
                    if sort_blocks(i[2]) == 1:
                        dictdelblocknum['Events'] += 1
                    if sort_blocks(i[2]) == 2:
                        dictdelblocknum['Looks'] += 1
                    if sort_blocks(i[2]) == 3:
                        dictdelblocknum['Control'] += 1
                    # if sort_blocks(i[2]) == 4:
                    #     dictdelblocknum['Sound'] += 1
                    if sort_blocks(i[2]) == 5:
                        dictdelblocknum['Sensing'] += 1
                    if sort_blocks(i[2]) == 6:
                        dictdelblocknum['Pen'] += 1
                    if sort_blocks(i[2]) == 7:
                        dictdelblocknum['Operatprs'] += 1
                    # if sort_blocks(i[2]) == 8:
                    #     dictdelblocknum['More'] += 1
                    if sort_blocks(i[2]) == 9:
                        dictdelblocknum['data'] += 1

    if 'delcosrec' in js:
        delcosrec = js['delcosrec']
        for i in delcosrec:
            if i:
                if i[1]=='dup':
                    dictdelcosnum['dup'] += 1
                if i[1]=='del':
                    dictdelcosnum['del'] += 1

    if 'addcosrec' in js:
        addcosrec = js['addcosrec']
        dictaddcosnum['add'] += 1
        for i in addcosrec:
            if i:
                if i[4] == 'lib':
                    dictaddcosnum['lib'] += 1
                if i[4] == 'paint':
                    dictaddcosnum['paint'] += 1
                if i[4] == 'computer':
                    dictaddcosnum['computer'] += 1
                if i[4] == 'photo':
                    dictaddcosnum['photo'] += 1

    if 'addbacrec' in js:
        addbacrec = js['addbacrec']
        dictaddbacnum['add'] += 1
        for i in addbacrec:
            if i:
                if i[4] == 'lib':
                    dictaddbacnum['lib'] += 1
                if i[4] == 'paint':
                    dictaddbacnum['paint'] += 1
                if i[4] == 'computer':
                    dictaddbacnum['computer'] += 1
                if i[4] == 'photo':
                    dictaddbacnum['photo'] += 1

    if 'delbacrec' in js:
        delbacrec = js['delbacrec']
        for i in delbacrec:
            if i:
                if i[1]=='dup':
                    dictdelbacnum['dup'] += 1
                if i[1]=='del':
                    dictdelbacnum['del'] += 1

    if 'addsprrec' in js:
        addsprrec = js['addsprrec']
        dictaddsprnum['add'] += 1
        for i in addsprrec:
            if i:
                if i[4] == 'lib':
                    dictaddsprnum['lib'] += 1
                if i[4] == 'paint':
                    dictaddsprnum['paint'] += 1
                if i[4] == 'computer':
                    dictaddsprnum['computer'] += 1
                if i[4] == 'photo':
                    dictaddsprnum['photo'] += 1

    if 'delsprrec' in js:
        delsprrec = js['delsprrec']
        for i in delsprrec:
            if i:
                if i[1]=='dup':
                    dictdelsprnum['dup'] += 1
                if i[1]=='del':
                    dictdelsprnum['del'] += 1
    if 'addsndrec' in js:
        addsndrec = js['addsndrec']
        dictaddsndnum['add'] += 1
        for i in addsndrec:
            if i:
                if i[4] == 'lib':
                    dictaddsndnum['lib'] += 1
                if i[4] == 'create':
                    dictaddsndnum['create'] += 1
                if i[4] == 'computer':
                    dictaddsndnum['computer'] += 1

    if 'delsndrec' in js:
        delsndrec = js['delsndrec']
        for i in delsndrec:
            if i:
                if i[1]=='dup':
                    dictdelsndnum['dup'] += 1
                if i[1]=='del':
                    dictdelsndnum['del'] += 1
    #
    # if 'changecos' in js:
    #     changecos = js['changecos']
    # if 'changespr' in js:
    #     changespr = js['changespr']
    # if 'changeop' in js:
    #     changeop = js['changeop']

    print(dictaddblocknum,"\n",dictdelblocknum,"\n",dictdelsprnum,"\n",dictaddsprnum,"\n",dictdoublocknum)
    return dictaddblocknum,dictdelblocknum,dictdelsprnum,dictaddsprnum,dictdoublocknum


if __name__ == '__main__':
    path = 'C:\\Users\\413knight\\Desktop\\Untitled Folder\\mproductions\\动态.sb2'
    getModule(path)