import os
import requests
import json
import re
import datetime
from multiprocessing import Queue
from copy import deepcopy
import time
from multiprocessing import Pool
"""这段代码在Linux下运行即可   用的进程"""

q = Queue()
PATH = os.getcwd()


q = Queue()


class Airsia_Handler_spider(object):
    '''start_year,start_month,start_day开始日期，end_year,end_month,end_day结束日期  表示几号到记号  从哪到哪的所有航班'''
    def __init__(self, start_year=2019, start_month='03', start_day='01', end_year=2019, end_month='03', end_day='02'):
        self.start_year = start_year
        self.start_month = start_month
        self.start_day = start_day
        self.end_year = end_year
        self.end_month = end_month
        self.end_day = end_day
        print("{}-{}-{}到{}-{}-{}的航班信息".format(self.start_year, self.start_month, self.start_day, self.end_year, self.end_month, self.end_day))

    def get_time(self, url):
        '''获取航班时间与另一个和与机票关联的id并返回列表'''
        headers = {
            'user-agent': "Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 71.0.3578.98Safari / 537.36",
        }
        print('正在请求时间页面：{}'.format(url))
        req = requests.get(url, headers=headers)
        li = []
        print("请求状态：{}".format(req.status_code))
        if req.status_code == 200:
            content = json.loads(req.text)
            print(content)
            for i in content:
                dic = {}
                dic['id'] = i['InventoryLegIdList']
                dic['arrTime'] = str(i['STD']).replace('-', '').replace(':', '').replace(' ', '')
                dic['depTime'] = str(i['STA']).replace('-', '').replace(':', '').replace(' ', '')

                li.append(dic)
        else:
            #错误日志
            with open(os.path.join(PATH, 'logging.log',), 'a+', encoding='utf-8') as f:
                f.write("{}  状态码：{}   url： {} \n".format(
                    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    req.status_code,
                    req.url))
        return li

    def get_price(self, url, li=[]):
        '''解析并获取航班信息并将每次航班信息添加入列表中并返回'''
        if li:
            headers = {
                'user-agent': "Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 71.0.3578.98Safari / 537.36",
                'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJBMXoyUWloUEtXSWdtYlJ3a0ExWXpHcjNobFZKN1hJMiIsImlhdCI6MTU0NDQzODIwOCwiZXhwIjoxNjA3NTk2NjA4LCJhdWQiOiJQV0EgRGV2Iiwic3ViIjoicHJhZGVlcGt1bWFyckBhaXJhc2lhLmNvbSJ9.QJPYvJvzx8IZFP6mYTAKwva7eQ_DVT_4JRwk75Uhhd8',
            }
            print('正在请求航班信息页面：{}'.format(url))
            req = requests.get(url, headers=headers)
            # 存数据的列表
            lis = []
            print("请求状态：{}".format(req.status_code))
            #请求状态为200  进行解析
            if req.status_code == 200:
                content = json.loads(req.text)
                print(content)
                price_infos = (content['GetAvailability'])
                for info in price_infos:
                    for dic in li:
                        new_dic = {}                #生成新字典用来保存数据  循环一次 生成一个  用于加入列表
                        #这个for循环用于匹配时间页的ID是否与航班信息的id相等   相等就解析  不同   跳出循环
                        for i in info['FaresInfo']:
                            if dic['id'] != i['InventoryLegs']:
                                continue

                            s = i['JourneySellKey']
                          #  print(s)
                            #起始地点   航班编号
                            start_end = re.findall(r'~([A-Z]+)~', s)
                            flightNumber = re.findall(r'~\^(\w+~\s?[0-9]+)~', s)
                            #出发时间  落地时间   从哪起飞   落地城市   航班编号   航班型号
                            new_dic['arrTime'] = dic['arrTime']
                            new_dic['depTime'] = dic['depTime']
                            new_dic['arrAirport'] = start_end[0]
                            new_dic['depAirport'] = start_end[-1]
                            new_dic['flightNumber'] = flightNumber[0].replace('~', '').replace(' ', '')
                            new_dic['carrier'] = flightNumber[0][:2]
                            #高价格仓位
                            if i['BrandedFares'].get('FlatBed'):
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
            else:
                # 错误日志
                with open(os.path.join(PATH, 'logging.log', ), 'a+', encoding='utf-8') as f:
                    f.write("{}  状态码：{}   url： {} \n".format(
                        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        req.status_code,
                        req.url))
            return lis
        else:
            return li

    def save_json(self, lis=[]):
        '''保存为json文件'''
        with open(os.path.join(PATH, 'Flightinformation.json'), 'a+') as f:
            for i in lis:
                print('正在写入{}'.format(i))
                f.write(json.dumps(i)+ '\n')

    def produce_url(self):
        """生产从几号到几号的所有url"""
        #5号-10号过了几天
        CITY_CODINGS = ['GAY', 'BNE', 'FUK', 'ATQ', 'AKL', 'MFM', 'PDG', 'IXB', 'DPS', 'UTP', '3AK', '3AA', 'BTJ', 'BLR',
              'PKU', 'PEK', 'PEN', 'BBI', 'IXC', 'CSX', 'MPH', 'CTU', 'CKG', 'CJM', 'KIX', 'DAC', 'DVO', 'TGG',
              'TRZ', 'NRT', 'HND', 'TST', 'TWU', 'PUS', 'PQC', 'KHH', 'KBR', '1AI', 'KCH', 'GAU', 'KUA', 'CAN',
              'KWL', 'GOI', 'HYD', 'HGH', 'HDY', 'HAN', 'ROI', 'SGN', 'HHQ', 'OOL', 'JED', 'KUL', 'CJU', 'KTM',
              'CCU', '3AD', 'KBV', 'SWA', 'PNH', 'PLM', 'KLO', '3AG', 'CGY', 'CRK', 'CMB', 'COK', 'LBJ', 'KKC',
              'KMG', 'PNK', 'UNN', '1AD', 'LGK', 'IXR', 'LPQ', 'LOE', '1AE', 'LOP', 'NST', '3AR', '3AE', 'MLE',
              'MNL', 'MDL', 'DMK', 'MYY', 'BOM', 'KNO', 'BTU', 'NGO', 'AVV', '3AC', 'NAG', 'KOP', 'NAW', 'LBU',
              'KHN', 'NKG', 'NNG', 'NNT', '1AF', 'NGB', '1AB', 'PHS', '1AC', 'PER', 'HKT', 'PPS', 'PNQ', 'MAA',
              '3AJ', 'CEI', 'CNX', 'VCA', 'JOG', 'SNO', '1AJ', 'SRG', 'SDK', 'PVG', 'SZX', 'SBW', 'ICN', 'SXR',
              'SUB', 'DTB', '3AB', 'URT', '3AI', '1AA', 'CEB', 'STV', 'SOC', 'TAG', 'TAC', 'TPE', 'HNL', '1AH',
              'TRV', 'TSN', 'BDO', 'UPG', 'VTZ', 'BWN', 'WUH', 'BFV', '3AV', 'UTH', 'UBP', 'XIY', 'KOS', 'SYD',
              'DAD', 'REP', 'HKG', '1AG', 'DEL', 'SIN', 'JHB', 'BKI', 'CGK', 'AOR', 'CXR', 'RGN', 'ILO', 'IPH',
              'IDR', 'IMF', 'VTE', 'CTS', 'JAI']                                                   #城市编码
        start_time = '{}-{}-{}'.format(self.start_year, self.start_month, self.start_day)
        end_time = '{}-{}-{}'.format(self.end_year, self.end_month, self.end_day)
        d1 = datetime.datetime.strptime(start_time, '%Y-%m-%d')
        d2 = datetime.datetime.strptime(end_time, '%Y-%m-%d')
        delta = int(str(d2 - d1).split(' ', 1)[0])
        li = []
        if delta >= 0:
            for day in range(0, delta+1):
                n_day = datetime.timedelta(days=day)
                n_days = str((d1 + n_day).strftime('%Y-%m-%d'))
              #  print(n_days)
                for city_code1 in CITY_CODINGS:
                    for city_code2 in CITY_CODINGS:
                        if city_code1 != city_code2:
                            go_time_url = "https://sch.apiairasia.com/schedule/{}/{}/{}/file.json".format(city_code1.lower(), city_code2.lower(), n_days)
                            go_price_url = 'https://k.airasia.com/shopprice/0/0/{}/{}/{}/1/0/0'.format(city_code1.lower(), city_code2.lower(), n_days)
                            li.append((go_time_url, go_price_url))
            print(len(li))
            return li
        else:
            return '输入有误'

    def queue_add_url(self, li=[]):
        """将生产的URL加入队列"""
        for url in li:
            q.put(url)

    def run(self):
        """将url从队列里取出来进行访问"""
        while True:
            if q.empty():
                break
            url = q.get()
            print(url)
            if url == "输入有误":
                continue
            go_time_req = self.get_time(url[0])
            go_price = self.get_price(url[1], go_time_req)
            print(go_price)
            self.save_json(go_price)
            #time.sleep(3)


if __name__ == "__main__":
    time1 = time.time()
    spider = Airsia_Handler_spider(
        start_year=2019,
        start_month='03',
        start_day='06',
        end_year=2019,
        end_month='03',
        end_day=15
    )
    urls = spider.produce_url()
    spider.queue_add_url(urls)
    pool = Pool(processes=10)
    for i in range(10):
        pool.apply_async(spider.run)
    spider.run()
    pool.close()
    pool.join()
    time2 = time.time()
    print(time2 - time1)
