import os
import requests
import json
import re
from lxml import etree
from multiprocessing import Queue
from copy import deepcopy



def get_address(address):
    ADDRESS = {
        '北京': 'pek',
        '天津': 'tsn',
        '西安': 'xiy',
        '成田': 'nrt',
        '羽田': 'gnd',
        '斗湖': 'twu'
    }
    return ADDRESS[address]


class Airsia_Handler_spider(object):
    def __init__(self, start='', end='', start_year=2019, start_month=3, start_day=1, end_year=2019, end_month=3, end_day=2 ):
        self.start = start
        self.end = end
        self.start_year = start_year
        self.start_month = start_month
        self.start_day = start_day
        self.end_year = end_year
        self.end_month = end_month
        self.end_day = end_day
        print("{}-->{} {}-{}-{}到{}-{}-{}的航班信息".format(self.start, self.end, self.start_year, self.start_month, self.start_day, self.end_year, self.end_month, self.end_day))

    def get_time(self, url):
        '''获取航班时间与另一个和与机票关联的id'''
        headers = {
            'user-agent': "Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 71.0.3578.98Safari / 537.36",
        }
        req = requests.get(url, verify=False, headers=headers)
        li = []
   #     print(req.status_code)
        if req.status_code == 200:
            content = json.loads(req.text)
            for i in content:
                dic = {}
                dic['id'] = i['InventoryLegIdList']
                dic['arrTime'] = str(i['STD']).replace('-', '').replace(':', '').replace(' ', '')
                dic['depTime'] = str(i['STA']).replace('-', '').replace(':', '').replace(' ', '')

                li.append(dic)
        return li

    def get_price(self, url, li=[]):
        '''获取航班信息'''
        headers = {
            'user-agent': "Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 71.0.3578.98Safari / 537.36",
            'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJBMXoyUWloUEtXSWdtYlJ3a0ExWXpHcjNobFZKN1hJMiIsImlhdCI6MTU0NDQzODIwOCwiZXhwIjoxNjA3NTk2NjA4LCJhdWQiOiJQV0EgRGV2Iiwic3ViIjoicHJhZGVlcGt1bWFyckBhaXJhc2lhLmNvbSJ9.QJPYvJvzx8IZFP6mYTAKwva7eQ_DVT_4JRwk75Uhhd8',
        }
        req = requests.get(url, verify=False, headers=headers)
        # 存数据的列表
        lis = []
      #  print(req.status_code)
        if req.status_code == 200:
            content = json.loads(req.text)
            price_infos = (content['GetAvailability'])
            for info in price_infos:
                for dic in li:
                    new_dic = {}
                    for i in info['FaresInfo']:
                        if dic['id'] != i['InventoryLegs']:
                            continue

                        s = i['JourneySellKey']
                        print(s)
                        #起始地点   航班编号
                        start_end = re.findall(r'~([A-Z]+)~', s)
                        flightNumber = re.findall(r'~\^(\w+~\s?[0-9]+)~', s)

                        new_dic['arrTime'] = dic['arrTime']
                        new_dic['depTime'] = dic['depTime']
                        new_dic['arrAirport'] = start_end[0]  # 从——起飞
                        new_dic['depAirport'] = start_end[-1]  # 落地城市——
                        print(start_end)
                        print(flightNumber)
                        new_dic['flightNumber'] = flightNumber[0].replace('~', '').replace(' ', '')  # 航班编号
                        new_dic['carrier'] = flightNumber[0][:2]    #航班型号
                        #高价格仓位
                        cabin = i['BrandedFares']['FlatBed']['FareSellKey']
                        price = i['BrandedFares']['FlatBed']['TotalPrice']
                        new_dic['cabin'] = cabin
                        new_dic["price"] = price
                        lis.append(new_dic)
                        #低价格仓位
                        cabin = i['BrandedFares']['LowFare']['FareSellKey']
                        price = i['BrandedFares']['LowFare']['TotalPrice']
                        copy_dic = deepcopy(new_dic)
                        copy_dic['cabin'] = cabin
                        copy_dic["price"] = price
                        lis.append(copy_dic)
              #  print(json.dumps(lis))
        return lis

    def save_json(self, lis=[]):
        '''保存为json文件'''
        path = os.getcwd()
        with open(os.path.join(path, 'Flightinformation.json'), 'a+') as f:
            for i in lis:
                f.write(json.dumps(i)+ '\n')

    def run(self):
        go_time_url = "https://sch.apiairasia.com/schedule/{}/{}/{}-{}-{}/file.json".format(
                        get_address(self.start),
                        get_address(self.end),
                        self.start_year,
                        self.start_month,
                        self.start_day
                )
        go_price_url = 'https://k.airasia.com/shopprice/0/0/{}/{}/{}-{}-{}/1/0/0'.format(
                        get_address(self.start),
                        get_address(self.end),
                        self.start_year,
                        self.start_month,
                        self.start_day,
                )

        print(go_time_url)
        print(go_price_url)
        go_time_req = self.get_time(go_time_url)
        go_price = self.get_price(go_price_url, go_time_req)

        self.save_json(go_price)


spider = Airsia_Handler_spider(start='北京', end='斗湖', start_year=2019, start_month='03', start_day='10', end_year=2019, end_month='03', end_day=12 )
spider.run()

