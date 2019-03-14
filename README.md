# yahang_spider
1：亚航网站的抓取
    需要在linux下运行  不知道为什么windows不能运行多进程
    
    
2：用pyspider抓取华丽志整站          
  1:pip install pyspider
  2:点击create_new_project
  3:将代码复制上去
  4：点击save
  5:回到直接面点击run即可
  6：pyspider可以选择是否开启多线程
  
  3：用scrapy写一个通用抽取静网站中的文章
    1：需要用到的库
      scrapy  
      jieba         用于中文分词      
        首先将文章和标题拼接  然后将文章进行分词，降序，然后将出现次数最大的前20个分词只要名词辞去出来，这20个分词重要 ，主要是用来进行数据的去重的
      re            相信大家都直达这个库是用来干嘛的
      pysqlite3     这个是用来将爬取后的数据存入sqlite3中
            自己单独写一个create_db脚本 用来创建splite3
      readablity   这个库是用来进行文章都抽取的   基于文章密度的算法 可能不太准确
  
