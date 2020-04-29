from selenium import webdriver
from time import sleep as sl #在爬蟲的時候，time常常會用到
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import re
import pymongo

client = pymongo.MongoClient('localhost',port = 27017)
db = client.txDataBase
collection = db.txDec

chrome_options = Options()  #啟動無頭模式
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(chrome_options = chrome_options)
driver.get("https://www.taifex.com.tw/cht/3/futDailyMarketReport")

driver.find_element_by_name("queryDate").clear() #必須先清空日期選擇項目
checkDate = driver.find_element_by_name("queryDate") #選擇日期
checkDate.send_keys(r"2019/12/31")
sl(1)
button = driver.find_element_by_name("button")
button.click()
sl(1)
selectop = Select(driver.find_element_by_name("MarketCode"))
selectop.select_by_value('0')
sl(1)
button = driver.find_element_by_name("button")
button.click()
sl(1)

for i in range(30):
    try:
        r_list = driver.find_elements_by_xpath('//*[@id="printhere"]/table/tbody/tr[2]/td/table[2]/tbody/tr')
        date = driver.find_element_by_xpath('//*[@id="printhere"]/table/tbody/tr[2]/td/h3') 
        dateString = re.findall("\d+[/]\d+[/]\d+",date.text)[0] #抓取日期，以便後續存入資料庫分辨

        xList = []
        for i in r_list:
	        #print(i.text) 驗證xpath是否正確
	        xList.append(i.text.split())

        titleList = xList[0]
        titleList[1] = ''.join(titleList[1:4])
        del titleList[2:4]
        titleList[5] = ''.join(titleList[5:7])
        del titleList[6]
        titleList.append("日期")

        del xList[-1] #小計的部分不需要
        xList = [i+[dateString] for i in xList]

        for i in xList[1:]:
           dataDict = {}
           for j,k in zip(titleList,i):
               dataDict[j] = k
           collection.insert(dataDict) 
        button = driver.find_element_by_name("button3")
        button.click()   
        sl(2)
    except Exception as e:
    	print(e)
    	button = driver.find_element_by_name("button3")
    	button.click()

driver.quit() #自動關閉
