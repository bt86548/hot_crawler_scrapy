import scrapy
import json, re
from scrapy import Request
from scrapy import settings
from scrapy import middleware
from scrapy import pipelines
from ..items import HotScrapyItem
'''啟動方式scrapy crawl hot_scrapy -o hot_scrapy.json'''
'''settings中預設download_delay為0.1'''


#change download_delay to 0.1 in settings.py, or will be banned by the website
class HotSpider(scrapy.Spider):
    name = "hot_scrapy"

    #allowed_domains = ['https://www.hotcar.com.tw/CWA/CWA050.html']

    def start_requests(self):
        url = "https://www.hotcar.com.tw/SSAPI45/API/SPRetB?Token=VfaU%2BLJXyYZp7Nr3mFhCQtBfZ%2FrL2AQmOjkOW4W1uZVumEKn0wIHcD%2FRsdkmgB8di2Y9HFgUS%2F7HFxHm4m9eACLvfBCTdBEGoGqcd6RDUeZNSwlOrVeFarS9bEalGyz6"
        data = {
            'PARMS': [
                "https://www.hotcar.com.tw",
                "https://www.hotcar.com.tw/image/nophoto.png", "", "", 0, 0,
                "", "", 0, 0, "", "", "", "", "", "", "", "", "", "", "", ""
            ],
            'SPNM':
            "CWA050Q1_2018",
            'SVRNM': ["HOTCARAPP"]
        }

        yield Request(url, self.parse, method="POST", body=json.dumps(data))

    def parse(self, response):
        url = "https://www.hotcar.com.tw/SSAPI45/API/SPRetB?Token=VfaU%2BLJXyYZp7Nr3mFhCQtBfZ%2FrL2AQmOjkOW4W1uZVumEKn0wIHcD%2FRsdkmgB8di2Y9HFgUS%2F7HFxHm4m9eACLvfBCTdBEGoGqcd6RDUeZNSwlOrVeFarS9bEalGyz6"
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'Cookie':
            '_ga=GA1.3.1392185054.1591847338; _gid=GA1.3.762883749.1591847338; __BWfp=c1591847338332xec3680f27; _gcl_au=1.1.1587304046.1591847338; _fbp=fb.2.1591847338370.673347900; Token=VfaU+LJXyYZp7Nr3mFhCQtBfZ/rL2AQmOjkOW4W1uZVumEKn0wIHcD/RsdkmgB8di2Y9HFgUS/7HFxHm4m9eACLvfBCTdBEGoGqcd6RDUeZNSwlOrVeFarS9bEalGyz6; clientID=1392185054.1591847338; Tagtoo_pta=pta_03+_&gpa+_&gpb+_&gpc+_&vip+_; _TUCI_T=sessionNumber+18426&pageView+18426&Search+18426; _TUCS=1; _gat_UA-11424410-1=1; _gat_UA-34980571-16=1; _TUCI=sessionNumber+12523&ECId+387&hostname+www.hotcar.com.tw&pageView+92454&Search+6000',
            'Referer':
            'https://www.hotcar.com.tw/SSAPI45/proxyPage/proxyPage.html'
        }
        data = json.loads(response.body)
        car_id = []
        for i in data['DATA']['Table1']:
            car_id.append(i[u'TSEQNO'])
        for j in range(len(car_id)):
            data2 = {
                'PARMS': [
                    car_id[j], "https://www.hotcar.com.tw",
                    "https://www.hotcar.com.tw/image/nophoto.png", "", ""
                ],
                'SPNM':
                "CWA060Q_2018",
                'SVRNM': ["HOTCARAPP"]
            }
            yield Request(url,
                          callback=self.by_car_crawler,
                          method="POST",
                          body=json.dumps(data2))

    def by_car_crawler(self, response):
        items = HotScrapyItem()
        data = json.loads(response.text)
        items['id'] = data['DATA']['Table1'][0][u'TSEQNO']
        items['source'] = 'hot'
        items['brand'] = data['DATA']['Table1'][0][u'BRANDNM'].title()
        items['type'] = data['DATA']['Table1'][0][u'CARTYPENM'].strip().lower()
        items[
            'link'] = 'https://www.hotcar.com.tw/CWA/CWA060.html?TSEQNO=' + str(
                data['DATA']['Table1'][0][u'TSEQNO'])
        items['year'] = data['DATA']['Table1'][0][u'CARYY']
        items['price'] = data['DATA']['Table1'][0][u'SALAMT1'].strip('萬')
        items['seller'] = data['DATA']['Table1'][0][u'NAME']
        items['kind'] = data['DATA']['Table1'][0][u'BODYTYPENM']
        items['sys'] = data['DATA']['Table1'][0][u'GEARTYPENM']
        items['color'] = data['DATA']['Table1'][0][u'CCORLORNM']
        items['locate'] = data['DATA']['Table1'][0][u"MCITYNM"]
        items['miles'] = data['DATA']['Table1'][0][u'KM1']
        items['cc'] = round(
            int(data['DATA']['Table1'][0]['CCNUM_R1'].replace(',', "")), -2)
        if data['DATA']['Table1'][0]['WDTYPENM'] == '二輪傳動':
            items['power'] = '2'
        elif data['DATA']['Table1'][0]['WDTYPENM'] == '四輪傳動':
            items['power'] = '4'
        else:
            items['power'] = None
        items['car_gas'] = data['DATA']['Table1'][0]["GASTYPENM"]
        items['safe_bag'] = '1' if data['DATA']['Table1'][0][
            u"EQUIP01"] == 'Y' else '0'
        items['abs'] = '1' if data['DATA']['Table1'][0][
            u"EQUIP02"] == 'Y' else '0'
        items['air_con'] = '1' if data['DATA']['Table1'][0][
            u"EQUIP03"] == 'Y' else '0'
        items['back_radar'] = '1' if data['DATA']['Table1'][0][
            u"EQUIP04"] == 'Y' else '0'
        items['back_screen'] = '1' if data['DATA']['Table1'][0][
            u"EQUIP05"] == 'Y' else '0'
        items['gps'] = '1' if data['DATA']['Table1'][0][
            u"EQUIP06"] == 'Y' else '0'
        items['window'] = '1' if data['DATA']['Table1'][0][
            u"EQUIP07"] == 'Y' else '0'
        items['auto_windows'] = '1' if data['DATA']['Table1'][0][
            u"EQUIP08"] == 'Y' else '0'
        items['auto_side'] = '1' if data['DATA']['Table1'][0][
            u"EQUIP09"] == 'Y' else '0'
        items['l_chair'] = '1' if data['DATA']['Table1'][0][
            u"EQUIP10"] == 'Y' else '0'
        items['alert'] = '1' if data['DATA']['Table1'][0][
            u"EQUIP11"] == 'Y' else '0'
        items['auto_chair'] = '1' if data['DATA']['Table1'][0][
            u"EQUIP12"] == 'Y' else '0'
        items['cd'] = '1' if data['DATA']['Table1'][0][
            u"EQUIP13"] == 'Y' else '0'
        items['media'] = '1' if data['DATA']['Table1'][0][
            u"EQUIP15"] == 'Y' else '0'
        items['ss'] = '1' if data['DATA']['Table1'][0][
            u"EQUIP16"] == 'Y' else '0'
        items['alu'] = '1' if data['DATA']['Table1'][0][
            u"EQUIP17"] == 'Y' else '0'
        items['hid'] = '1' if data['DATA']['Table1'][0][
            u"EQUIP18"] == 'Y' else '0'
        items['tpms'] = '1' if data['DATA']['Table1'][0][
            u"EQUIP21"] == 'Y' else '0'
        items['fog_lights'] = '1' if data['DATA']['Table1'][0][
            u"EQUIP22"] == 'Y' else '0'
        items['ldws'] = '1' if data['DATA']['Table1'][0][
            u"EQUIP23"] == 'Y' else '0'
        items['blind_spot'] = '1' if data['DATA']['Table1'][0][
            u"EQUIP24"] == 'Y' else '0'
        items['electric_tailgate'] = '1' if data['DATA']['Table1'][0][
            u"EQUIP25"] == 'Y' else '0'
        items['silde_door'] = '1' if data['DATA']['Table1'][0][
            u"EQUIP26"] == 'Y' else '0'
        items['whole_window'] = '1' if data['DATA']['Table1'][0][
            u"EQUIP27"] == 'Y' else '0'
        items['key_less'] = '1' if data['DATA']['Table1'][0][
            u"EQUIP28"] == 'Y' else '0'
        items['isofix'] = '1' if data['DATA']['Table1'][0][
            u"EQUIP29"] == 'Y' else '0'
        items['lcd'] = '1' if data['DATA']['Table1'][0][
            u"EQUIP30"] == 'Y' else '0'
        items['shift_paddles'] = '1' if data['DATA']['Table1'][0][
            u"EQUIP31"] == 'Y' else '0'
        items['es'] = '1' if data['DATA']['Table1'][0][
            u"EQUIP32"] == 'Y' else '0'
        items['led'] = None
        items['trc'] = None
        items['tcs'] = None
        items['ldws'] = None
        items['aeb'] = None
        items['acc'] = None
        items['hud'] = None
        items['multi_wheel'] = None
        items['auto_park'] = None
        items['people'] = None
        items['female_used'] = None
        items['turbo'] = None
        items['warranty'] = None
        items['epb'] = None
        items['clc'] = None

        yield items


# "EQUIP01": "N", 安全氣囊 (0) safe_bag
# "EQUIP02": "N", abs abs
# "EQUIP03": "N", 恆溫空調 air_con
# "EQUIP04": "N", 倒車雷達 back_radar
# "EQUIP05": "N", 倒車影像 back_screen
# "EQUIP06": "N", gps gps
# "EQUIP07": "N", 天窗 window
# "EQUIP08": "N", 電動窗 auto_windows
# "EQUIP09": "N", 電動後視鏡 auto_side
# "EQUIP10": "N", 皮椅 l_chair
# "EQUIP11": "N", 防盜器 alert
# "EQUIP12": "N", 電動座椅 auto_chair
# "EQUIP13": "N", CD cd
# "EQUIP14": "N", VCD 刪除
# "EQUIP15": "N", DVD media
# "EQUIP16": "N", 定速系統 ss
# "EQUIP17": "N", 鋁圈 alu
# "EQUIP18": "N", HID hid
# "EQUIP19": "N", Push Start 刪除
# "EQUIP20": "N", Hybrid 刪除
# "EQUIP01MEMO": "" 刪除
# "EQUIP12MEMO": "" 刪除
# "EQUIP21": "N", 胎壓偵測 tpms
# "EQUIP22": "N", 霧燈 fog_lights
# "EQUIP23": "N", 車道偏移系統 ldws
# "EQUIP24": "N", 車道盲點偵測系統 blind_spot
# "EQUIP25": "N", 電動尾門 electric_tailgate
# "EQUIP26": "N", 電動滑門 silde_door
# "EQUIP27": "N", 全景window whole_window
# "EQUIP28": "N", Push Start key_less
# "EQUIP29": "N", ISOFIX isofix
# "EQUIP30": "N", 液晶螢幕 lcd
# "EQUIP31": "N", 方向盤換檔撥片 shift_paddles
# "EQUIP32": "N", ESP es
