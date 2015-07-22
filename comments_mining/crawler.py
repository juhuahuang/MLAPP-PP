# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2013, 2014 ppzc Inc.
# Author: am <hzd0107@hotmail.com>
# Version: Id:  ppData shenzhouPrice,v 0.1
# FileName: shenzhouPrice.py
# Date: <2014-10-16>
# Description: ppData


import lxml.etree as etree
import lxml.html.soupparser as soupparser
import urlparse
import urllib2
import urllib
import uuid
import os
import sys
sys.path.append('../lib')
import traceback
import json
import time
import mydb as localDb
import re
from htmlentitydefs import name2codepoint as n2cp
import mymail

RE_HTML_ENTITY = re.compile(r'&(#?)(x?)(\w+);', re.UNICODE)
cityListUrl = 'http://service.zuche.com/city/getCountryDepJson.do'

proxyServer = {"http": "http://10.130.145.102:80"}
proxyDesktop = {"http": "http://proxy.tencent.com:8080"}
curProxy = proxyDesktop

def loadNameMappingFile(inputFilePath):
    mapping=dict()
    for line in open(inputFilePath):
    # 奔驰E260L car_10  m27     奔驰    @
        items=line.decode("utf-8","ignore").strip('\n').split()
        if len(items)>=3:
            name=items[0]
            make=items[1]
            model=items[2]
            mapping[name]=(make,model)
    return mapping
nameMapping=loadNameMappingFile('shenzhouNameMapping.txt')

def decodeHtmlEntity(text):
    """
    Decode HTML entities in text, coded as hex, decimal or named.
    :param text:
    :return:
    """

    def substitute_entity(match):
        ent = match.group(3)
        if match.group(1) == "#":
            # decoding by number
            if match.group(2) == '':
                # number is in decimal
                return unichr(int(ent))
            elif match.group(2) == 'x':
                # number is in hex
                return unichr(int('0x' + ent, 16))
        else:
            # they were using a name
            cp = n2cp.get(ent)
            if cp:
                return unichr(cp)
            else:
                return match.group()

    try:
        return RE_HTML_ENTITY.sub(substitute_entity, text)
    except:
        return text


def isValidXmlCharOrdinal(i):
    """
    判断字符是不是xml的合法字符
    XML standard defines a valid char as::
    Char ::= #x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD] | [#x10000-#x10FF                                                                                                                                                             FF]
    @param i: unicode char
    @return:True if valid else False
    """
    return (
        0x20 <= i <= 0xD7FF
        or i in (0x9, 0xA, 0xD)
        or 0xE000 <= i <= 0xFFFD
        or 0x10000 <= i <= 0x10FFFF
    )


def cleanXmlString(s):
    """
    清除字符串s中不符合xml规范的字符
    参考：http://stackoverflow.com/questions/8733233/filtering-out-certain-bytes                                                                                                                                                             -in-python
    @param s: unicode
    @return:unicode
    """
    return ''.join(c for c in s if isValidXmlCharOrdinal(ord(c)))


class XpathDetail(object):
    def __init__(self, strValue):
        items = strValue.strip().split("`")
        if len(items) >= 3:
            self.valueType = int(items[0])

            self.path = items[1].strip()
            self.att = items[2].strip()

    def isValid(self):
        if self.path:
            return True
        else:
            return False


class Rule(object):
    '''
    描述各类型数据抓取的页面规则
    '''
    WORD_TYPE_PERSON = 0
    WORD_TYPE_ENTITY = 1
    VALUE_TYPE_TEXT = 0
    VALUE_TYPE_FILE = 1
    VALUE_TYPE_URL = 2


    @classmethod
    def itemDetailParse(self, strValue):
        """

        @param strValue:
        """
        index = strValue.find(":")
        if index > 0 and index + 1 < len(strValue):
            itemName = strValue[:index]
            pathChain = []
            pathChainStrs = strValue[index + 1:].split('^')
            for pathChainStr in pathChainStrs:
                if pathChainStr.strip():
                    pathDetail = XpathDetail(pathChainStr)
                    if pathDetail.isValid():
                        pathChain.append(pathDetail)
            return itemName, pathChain
        return None, None

    def __init__(self, line):
        """
        用一个字符串初始化一个规则
        @param line: str ,
            line 格式：wordType \t class1 \t class2 \t url \t termBaseXPath \t p                                                                                                                                                             ageCoding \t {itemDetail1} \t {itemDetail2}
            itemDetail 格式：itemName:{pathChain}
            pathChain 格式：{path}^{path}
            path 格式：valueType`xpath`name
        eg：
        0   12  122 http://top.baidu.com/buzz?b=238 //*[@id="main"]/div[2]/div/t                                                                                                                                                             able/tr gbk title:0`td[2]/a[1]`
        img:2`td[2]/a[1]`href^1`//*[@id="main"]/div[2]/div/div[2]/div[1]/div/div                                                                                                                                                             [2]/div/div/div[1]/a/img`src
        """
        items = line.strip().split("\t")
        if len(items) >= 7:
            self.wordsType = items[0].strip()
            self.classId1 = items[1].strip()
            self.classId2 = items[2].strip()
            self.url = items[3].strip()
            self.termXpath = items[4]
            self.coding = items[5]
            self.itemDetail = dict()
            # print len(items)
            for item in items[6:]:
                itemName, pathChain = Rule.itemDetailParse(item)
                print itemName, pathChain
                if itemName and pathChain:
                    self.itemDetail[itemName] = pathChain
            self.valid = True
        else:
            self.valid = False


def fetchData(rule, tempFileSaveDir=""):
    '''
    根据给定的规则拉取数据
    @param rule:Rule
    @param tempFileDir:
    @return:
    '''
    result = []
    print "starting"
    print "fetch :", rule.url, rule.itemDetail.keys()
    if not rule.valid:
        return result
    else:
        dom,responseHeader = getPageHtml(rule.url, pageCoding=rule.coding)
        #print etree.tostring(dom)
        if dom is None:
            return result
        for ele in dom.xpath(rule.termXpath):
            valueDict = dict()
            for itemName in rule.itemDetail:
                print "start fetch :", itemName, 50 * "*"
                curDom = ele
                pathChain = rule.itemDetail[itemName]
                for xpathDetail in pathChain:
                    value = getDataFromDom(curDom, xpathDetail)
                    print value
                    if value is not None:
                        if xpathDetail.valueType == Rule.VALUE_TYPE_TEXT:
                            valueDict[itemName] = value.replace("\t", " ").repla                                                                                                                                                             ce("\r", " ").replace("\n", " ")
                            break
                        elif xpathDetail.valueType == Rule.VALUE_TYPE_FILE:
                            rIndex = value.rfind(".")
                            fileType = ".jpg"
                            if rIndex >= 0 and rIndex + 1 < len(value):
                                fileType = value[rIndex:]
                                if len(fileType) > 5:
                                    fileType = ".jpg"
                            saveName = str(uuid.uuid1()).replace("-", "") + file                                                                                                                                                             Type
                            getFile(value, os.path.join(tempFileSaveDir, saveNam                                                                                                                                                             e))
                            valueDict[itemName] = saveName
                            break
                        elif xpathDetail.valueType == Rule.VALUE_TYPE_URL:
                            newUrl = value
                            if value.startswith("./"):
                                urlInfo = urlparse.urlparse(rule.url)
                                baseUrl = urlInfo.scheme + "://" + urlInfo.netlo                                                                                                                                                             c
                                newUrl = baseUrl + newUrl[1:]
                            curDom,responseHeader = getPageHtml(newUrl, pageCodi                                                                                                                                                             ng=rule.coding)
            result.append(valueDict)
    return result


def getDataFromDom(dom, xpathDetail):
    if dom is None:
        return None
    path = xpathDetail.path
    att = xpathDetail.att.strip()
    itemDom = dom.xpath(path)
    if not itemDom:
        return None
    else:
        if not att:
            return itemDom[0].text_content()
        if att in itemDom[0].keys():
            return itemDom[0].get(att, "")
        elif att in etree.tostring(itemDom[0]):
            return getAttFromStr(att, etree.tostring(itemDom[0]))
        else:
            return None

def getAttFromStr(att, line):
    """
    从字符串中获取属性信息
    @param att:
    @param line:
    @return:
    """
    attSymbol = " " + att + "="
    index = line.find(attSymbol)
    if index >= 0:
        tmpLine = line[index + len(attSymbol):].strip()
        symbol = tmpLine[0]
        symbolIndex = tmpLine.find(symbol, 1)
        if symbolIndex >= 1:
            tmpResult = tmpLine[1:symbolIndex]
            tmpResult = decodeHtmlEntity(tmpResult)
            return tmpResult
    return ""


def getPageHtml(url, enableProxy=False, parsed=True, pageCoding="utf-8", headers                                                                                                                                                             =None, data=None,timeout=10):
    '''
    获取指定的的页面，由soupparser进行转换，转换为htmlElement对象
    @param parsed: 是否进行转换
    @param url: 页面url
    @param enableProxy:是否启用代理
    @param pageCoding:页面编码
    @return:str if not parsed else lxml.html.htmlElement
    '''
    dt=None
    if data:
        dt=urllib.urlencode(data)
    proxyHandler = urllib2.ProxyHandler({"http": "http://127.0.0.1:8087"})
    noProxyHandler = urllib2.ProxyHandler({})
    if enableProxy:
        opener = urllib2.build_opener(proxyHandler)
    else:
        opener = urllib2.build_opener(noProxyHandler)
    urllib2.install_opener(opener)
    try:
        if not headers:
            result=urllib2.urlopen(url, data=dt,timeout=timeout)
            pageContent = result.read()

        else:
            request = urllib2.Request(url,headers=headers)
            print url
            result = urllib2.urlopen(request, timeout=timeout, data=dt)
            # print type(result)
            # print result
            pageContent = result.read()
            pageContent = pageContent.decode(pageCoding, "ignore")
        responseHeader=result.info()
    except:
        print "failed get page:", url
        return None,None
    if not parsed:
        pageContent = cleanXmlString(pageContent)
        return pageContent,responseHeader
    if pageContent:
        if pageCoding:
            # print "coding", pageCoding
            pageContent = pageContent.decode(pageCoding, "ignore")
            #print pageContent
        pageContent = cleanXmlString(pageContent)
        # try:
        soup = soupparser.fromstring(pageContent)
        # except Exception as e:
        # soup=None
        #     print "get page failed:",url
        #     traceback.print_stack()
        #     format_exception(e)
        return soup,responseHeader
    else:
        return None,responseHeader


def getFile(fileUrl, savePath, enableProxy=True):
    '''
    获取图片并保存
    @param fileUrl:
    @param savePath:文件保存位置
    @param enableProxy: 是否启动代理
    @return:
    '''
    print "get file:", fileUrl
    proxyHandler = urllib2.ProxyHandler({"http": "http://10.130.145.102:80"})
    noProxyHandler = urllib2.ProxyHandler({})
    if enableProxy:
        opener = urllib2.build_opener(proxyHandler)
    else:
        opener = urllib2.build_opener(noProxyHandler)
    urllib2.install_opener(opener)
    try:
        f = urllib2.urlopen(fileUrl)
        with open(savePath, "wb", True) as saveFile:
            saveFile.write(f.read())
    except:
        print "error while downloading file:", fileUrl


def getData(configFilePath, outputFilePath, fileSavingDir):
    """

    @param configFilePath:
    @param outputFilePath:
    @param fileSavingDir:文件保存位置
    @return:
    """
    rules = []
    for line in open(configFilePath, 'r', True):
        tmpLine = line.decode("utf-8", "ignore").strip()
        if tmpLine.strip():
            rule = Rule(tmpLine)
            if rule and rule.valid:
                rules.append(rule)

    resultFile = open(outputFilePath, 'w', True)
    for rule in rules:
        print "new rule"
        result = fetchData(rule, fileSavingDir)
        outputHead = str(rule.wordsType) + "\t" + rule.classId1 + "\t" + rule.cl                                                                                                                                                             assId2
        if len(result):
            for item in result:
                outputTail = "\t".join(name + ":" + value.replace('\t', " ").rep                                                                                                                                                             lace('\r', " ") for name, value in item)
                resultFile.write(outputHead + "\t" + outputTail + "\n")
    resultFile.close()


def getCityList():
    result = []
    content,responseHeader = getPageHtml(cityListUrl, enableProxy=False, parsed=                                                                                                                                                             False)
    jsonObject = json.loads(content, 'utf-8')
    for i in jsonObject:
        if i == 'countryDeps':
            for item in jsonObject[i]:
                cityDeps = item['cityDeps']
                # "provinceid": 2, "provincename": "吉林省", "provincesimplename                                                                                                                                                             ": "吉"
                provinceId = item['provinceid']
                provinceName = item['provincename']
                provinceSimpleName = item['provincesimplename']
                for ct in cityDeps:
                    # "cityenname": "Changchun", "cityid": 23, "cityname": "长春                                                                                                                                                             ", "depcount": 17
                    cityEnName = ct.get('cityenname', '')
                    cityId = ct.get('cityid', -1)
                    cityName = ct.get('cityname', '')
                    cityInfo = {'provinceId': provinceId, 'provinceName': provin                                                                                                                                                             ceName,
                                'provinceSimpleName': provinceSimpleName, 'cityI                                                                                                                                                             d': cityId,
                                'cityEnName': cityEnName, 'cityName': cityName}
                    result.append(cityInfo)

        else:
            # "cityenname": "shanghai", "cityid": 6, "cityname": "上海", "depcou                                                                                                                                                             nt": 16, "districtDeps":
            for item in jsonObject[i]:
                cityEnName = item['cityenname']
                cityId = item['cityid']
                cityName = item['cityname']
                districtDeps = item['districtDeps']
                cityInfo = {'cityId': cityId, 'cityEnName': cityEnName, 'cityNam                                                                                                                                                             e': cityName}
                result.append(cityInfo)
                # for ds in districtDeps:
                # # {"districtDepcount": 12, "districtid": 34, "districtname": "                                                                                                                                                             徐汇区"}
                #     districtId=ds['districtid']
                #     districtName=ds['districtname']
                #     disObj={'cityId':cityId,'cityEnName':cityEnName,'cityName'                                                                                                                                                             :cityName,
                #             'districtId':districtId,'districtName':districtNam                                                                                                                                                             e}
                #     result.append(disObj)
    return result


def getStore(cityList, storeConfigFilePath, fileSavingDir):
    result = []
    rules = []
    storeFile=open('stores.txt','w',True)
    for line in open(storeConfigFilePath, 'r', True):
        tmpLine = line.decode("utf-8", "ignore").strip()
        if tmpLine.strip():
            rule = Rule(tmpLine)
            if rule and rule.valid:
                rules.append(rule)
    citySet = cityList
    for rule in rules:
        while citySet:
            print len(citySet),"cities left"
            cityInfo = citySet.pop(0)
            try:
                if 'cityEnName' in cityInfo:
                    cityEnName = cityInfo['cityEnName']
                    cityName = cityInfo['cityName']
                    cityId = cityInfo['cityId']
                    # 'provinceId':provinceId,'provinceName':provinceName,
                    # 'provinceSimpleName':provinceSimpleName,
                    provinceName = cityInfo.get('provinceName', cityName)
                    provinceId = cityInfo.get('provinceId', "0")
                    provinceSimpleName = cityInfo.get('provinceSimpleName', '')
                    url = 'http://' + cityEnName.lower() + '.zuche.com/'
                    rule.url = url
                    print rule.url
                    tmpResult = fetchData(rule, fileSavingDir)
                    for rItem in tmpResult:
                        if 'storeId' in rItem and 'storeName' in rItem:
                            storeName = rItem.get('storeName', '')
                            storeId = rItem.get('storeId', '').replace(url, '').                                                                                                                                                             strip()
                            if storeName:
                                ob = {'storeName': storeName, 'storeId': storeId                                                                                                                                                             }
                                ob['cityEnName'] = cityEnName
                                ob['cityName'] = cityName
                                ob['cityId'] = cityId
                                ob['provinceName'] = provinceName
                                ob['provinceId'] = provinceId
                                ob['provinceSimpleName'] = provinceSimpleName
                                result.append(ob)
                                lineItem=(provinceId,provinceName,provinceSimple                                                                                                                                                             Name,cityName,cityId,
                                          cityEnName,storeId,storeName)
                                line="\t".join(str(t) for t in lineItem)
                                storeFile.write(line+"\n")
            except:
                citySet.append(cityInfo)
                print 'get store failed:',cityInfo['cityName']
    storeFile.close()
    return result


def getCarPrice(storeList, carConfigFilePath=None, fileSavingDir=None):
    ds=time.strftime('%Y-%m-%d')
    result = []
    storeSet = storeList
    print len(storeSet)
    resultFile=open("carPriceShenzhou.txt",'a',True)
    failedDict=dict()
    while storeSet:
        storeInfo = storeSet.pop(0)
        try:
            if 'cityId' in storeInfo:
                cityEnName = storeInfo['cityEnName']
                cityName = storeInfo['cityName']
                cityId = storeInfo['cityId']
                # 'provinceId':provinceId,'provinceName':provinceName,
                # 'provinceSimpleName':provinceSimpleName,
                provinceName = storeInfo.get('provinceName', cityName)
                provinceId = storeInfo.get('provinceId', cityId)
                provinceSimpleName = storeInfo.get('provinceSimpleName', '')
                storeName = storeInfo['storeName']
                storeId = storeInfo['storeId']
                url = 'http://order.zuche.com/border-%s-%s' % (cityId, storeId)
                tmpResult = getStoreCars(url)
                print len(tmpResult),'records get!'
                for item in tmpResult:
                    ob = item
                    ob['cityName'] = cityName
                    ob['cityEnName'] = cityEnName
                    ob['cityName'] = cityName
                    ob['cityId'] = cityId
                    ob['provinceName'] = provinceName
                    ob['provinceId'] = provinceId
                    ob['provinceSimpleName'] = provinceSimpleName
                    ob['storeId'] = storeId
                    ob['storeName'] = storeName
                    ob['ds']=ds
                    make,model=nameMapping.get(ob.get('name',''),(None,None))
                    if make:
                        ob['make']=make
                    if model:
                        ob['model']=model
                    st=json.dumps(ob)
                    resultFile.write(st+"\n")

                    result.append(ob)
        except:

            fStoreId=storeInfo['storeId']
            failedDict.setdefault(fStoreId,0)
            failedDict[fStoreId]+=1
            if failedDict[fStoreId]<3:
                storeSet.append(storeInfo)
            time.sleep(5)
            print 'get store cars failed:', storeInfo['storeId']
    resultFile.close()
    return result


def getStoreCars(url):
    print url
    result=[]
    # resultFile=open("carPriceShenzhou.txt",'a')
    carListUrl='http://order.zuche.com/order/carList.do'
    page,responseHeader = getPageHtml(url, enableProxy=False)
    setCookie=responseHeader.get('Set-Cookie',"")
    dmzSessionId=''
    if ';' in setCookie:
        dmzSessionId=setCookie.split(";")[0]
    uKeyXpath = '//*[@id="_form_uniq_id"]'
    att = 'value'
    uKey = ''
    itemDom = page.xpath(uKeyXpath)
    if att in itemDom[0].keys():
        uKey = itemDom[0].get(att, "")
    elif att in etree.tostring(itemDom[0]):
        uKey = getAttFromStr(att, etree.tostring(itemDom[0]))
    if uKey:
        print uKey
        time.sleep(2)
        """
        Accept:application/json, text/javascript, */*; q=0.01
        Accept-Encoding:gzip,deflate,sdch
        Accept-Language:zh-CN,zh;q=0.8,en;q=0.6
        Cache-Control:max-age=0
        Connection:keep-alive
        Content-Length:42
        Content-Type:application/x-www-form-urlencoded
        Cookie:bdshare_firstime=1413462629460; dmz-sessionid=cefcc820-f7bb-4f7e-                                                                                                                                                             9c37-0606ce3b5921; WT_FPC=id=28022c8aa197f3946e71407856398319:lv=1413467813910:s                                                                                                                                                             s=1413467619877
        Host:order.zuche.com
        Origin:http://order.zuche.com
        Referer:http://order.zuche.com/border-1-1469
        User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML                                                                                                                                                             , like Gecko) Chrome/34.0.1847.131 Safari/537.36
        X-Requested-With:XMLHttpRequest
        Form Dataview parsed
        formToken=X1QWiTNTLiBkt7ASaaiDr9vdlP4lhV0X
        """
        headers = {}
        headers['Referer'] = ""
        headers['Accept'] = "application/json, text/javascript, */*; q=0.01"
        # headers['Accept-Encoding']='gzip,deflate,sdch'
        headers['Connection'] = 'keep-alive'
        cookieStr="bdshare_firstime=1410866980091;realName=%E9%87%8D%E8%80%B3;"
        cookieStr+=dmzSessionId+"; WT_FPC=id=2a97c0788ed27ef4afb1410866376097:"
        timestamp=str(int(1000*time.time()))
        #"lv=1413474942648":ss=1413471542663"
        cookieStr+='lv='+timestamp+":ss=1413511062167"
        headers['Cookie'] =cookieStr
                           #'bdshare_firstime=1413462629460; dmz-sessionid=5e393                                                                                                                                                             25f-8903-47c9-9d02-b6a84f0baf62; WT_FPC=id=28022c8aa197f3946e71407856398319:lv=1                                                                                                                                                             413474942648:ss=1413471542663'
        headers['Host'] = 'order.zuche.com'
        headers[
            'User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537                                                                                                                                                             .36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
        headers['Origin']='http://order.zuche.com'
        data = {'formToken': uKey}

        content,responseHeader = getPageHtml(carListUrl, parsed=False,enableProx                                                                                                                                                             y=False, headers=headers, data=data)
        if content:
            jsonObj = json.loads(content, encoding='utf-8')
            result = jsonObj.get('result', {}).get('models', [])
            # print result
            # for item in result:
            #     s=json.dumps(item)
            #     resultFile.write(s+"\n")

    # resultFile.close()
    return result

def loadStores(inputFilePath):
    result=[]
    for line in open(inputFilePath,'r',True):
        items=line.decode("utf-8","ignore").strip().split("\t")
        if len(items)==8:
            provinceId,provinceName,provinceSimpleName,cityName,cityId,cityEnNam                                                                                                                                                             e,storeId,storeName=items
            names=['provinceId','provinceName','provinceSimpleName','cityName','                                                                                                                                                             cityId','cityEnName','storeId','storeName']
            ob=dict(zip(names,items))
            result.append(ob)
    return result

def storeData(carPriceFilePath):
    result=[]
    failed=[]
    db=localDb.get_db()
    for line in open(carPriceFilePath):
        tmpLine=line.strip()
        ob=json.loads(tmpLine)
        # print ob
        result.append(ob)
        if len(result)==100:
            errorCode=db.insert_many('price_shenzhou',result)
            db.commit()
            if errorCode==-1:
                failed.extend(result)
            result=[]
    failed.extend(result)
    for item in failed:
        db.insert('price_shenzhou',item)
    db.commit()
    db.close()

def updateMakeAndModel():
    db=localDb.get_db()
    sql='select * from price_shenzhou'
    data=db.exec_sql(sql)
    for item in data:
        ob=item
        make,model=nameMapping.get(ob.get('name',''),(None,None))
        if make:
            ob['make']=make
        if model:
            ob['model']=model
        db.insert('price_shenzhou',ob,False)
    db.commit()
    db.close()

def inform(data):
    cli=mymail.MyMail()
    mailReceiver='huzhidong@ppzuche.com'
    title = u"【报警】神州租车数据抓取错误"
    imgFiles = ''
    cli.send(mailReceiver, title, data, '', imgFiles)

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding("utf-8")
    cityList = getCityList()
    if len(cityList)<10:
        inform(u'神州租车数据城市抓取数量太少！！')
    #print cityList
    storeList = getStore(cityList, 'store.config', "data")
    if len(storeList)<100:
        inform(u'神州租车数据门店抓取数量太少！！')
    #storeList=loadStores('stores.txt')
    result=getCarPrice(storeList)
    if len(result)<10000:
        inform(u'神州租车数据门店车辆价格数据量小于预期！！')
    storeData('carPriceShenzhou.txt')
    # storeData(result)
    #updateMakeAndModel()
