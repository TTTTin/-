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


def getArray(argv):
    raw_json = unzip_scratch(argv)
    js = json.loads(raw_json)
    # print(js)
    if not js:
        return

    listforaddblock=[]
    listfordelblock=[]
    listforBackdrop=[]
    listforChange=[]
    listforChangeOp=[]
    listforCostume=[]
    listfordelbac=[]
    listfordelcos=[]
    listfordelspr=[]
    listforDoubleclickBlock=[]
    listforSound= []
    listforSpr=[]
    listfordelsnd=[]
    if 'addblockrec' in js:
        listforaddblock = js['addblockrec']
    if 'delblockrec' in js:
        listfordelblock = js['delblockrec']
    if 'addcosrec' in js:
        listforCostume = js['addcosrec']
    if 'delcosrec' in js:
        listfordelcos = js['delcosrec']
    if 'addbacrec' in js:
        listforBackdrop = js['addbacrec']
    if 'delbacrec' in js:
        listfordelbac = js['delbacrec']
    if 'addsprrec' in js:
        listforSpr = js['addsprrec']
    if 'delsprrec' in js:
        listfordelspr = js['delsprrec']
    if 'addsndrec' in js:
        listforSound = js['addsndrec']
    if 'delsndrec' in js:
        listfordelsnd = js['delsndrec']
    if 'changeop' in js:
        listforChangeOp = js['changeop']
    if 'doubleclick' in js:
        listforDoubleclickBlock = js['doubleclick']
    if 'changecos' in js:
        for i in js['changecos']:
            if i:
                listforChange.append(i)
    if 'changespr' in js:
        for i in js['changespr']:
            if i:
                listforChange.append(i)
    if 'changesnd' in js:
        for i in js['changesnd']:
            if i:
                listforChange.append(i)
    #print(listforChange, listforChangeOp)
    return listforaddblock, listfordelblock, listforBackdrop, listforChange, listforChangeOp,listforCostume, listfordelbac, listfordelcos, listfordelspr,listforDoubleclickBlock, listforSound, listforSpr,listfordelsnd


if __name__ == '__main__':
    getArray(sys.argv[1])
    # path = 'C:\\Users\\413knight\\Desktop\\Untitled Folder\\mproductions\\动态.sb2'
    # getArray(path)