import datetime, sys, re, csv, io, os
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep

en_url_base = "http://hboasia.com/HBO/en-tw/schedule/"
zh_url_base = "http://hboasia.com/HBO/zh-tw/schedule/"
channel = "hbo"
hbo, signature, family, hits, cinemax = [],[],[],[],[]
schedule = {"font_block_hbo":hbo, "font_block_signature":signature,
	"font_block_family":family, "font_block_hits":hits,
	"font_block_cinemax":cinemax}
chList = ["font_block_hbo", "font_block_signature",
		  "font_block_family", "font_block_hits",
		  "font_block_cinemax"]

def textTime(textTime):
	#convert show time on the website
	pos = textTime.index(":")
	hour, minute, ampm = int(textTime[:pos]), textTime[(pos+1):(pos+3)], textTime[-2:]
	adjust = 0
	if ampm.lower() == "am" and hour == 12:
		adjust = -12
	elif ampm.lower() == "pm" and hour == 12:
		adjust = 0
	elif ampm.lower() == "pm":
		adjust = 12

	return "{0}:{1}".format(hour+adjust, minute)

def dateStr(strDate):
	nums = re.findall(r'\d+', strDate)
	return datetime.datetime(int(nums[0]),int(nums[1]),int(nums[2]))

def getLinkInfo(driver, link_url):
	driver.get(link_url)
	sleep(2)
	htmlText = driver.page_source.encode("utf-8")
	fullText = BeautifulSoup(htmlText)
	findInfo = fullText.find_all("div", "special_font")
	info = ""
	for item in findInfo:
		if len(item["class"]) != 1:
			continue
		else:
			info = item.get_text()
			break
	if info == "":
		try:
			info = fullText.find("p","special_font").get_text()
		except:
			pass
	return info

def scrape(url_start, days):

	enDriver = webdriver.PhantomJS("phantomjs")
	zhDriver = webdriver.PhantomJS("phantomjs")
	infoDriver = webdriver.PhantomJS("phantomjs")

	for d in range(days):
		date = url_start + datetime.timedelta(days=d)
		url_date = "{0}/{1}/{2}".format(date.year, date.month, date.day)
		print "loading {0} data...".format(url_date)
		zh_url = "{0}{1}".format(zh_url_base,url_date)
		en_url = "{0}{1}".format(en_url_base,url_date)
		enDriver.get(en_url)
		zhDriver.get(zh_url)
		sleep(3)

		enText = enDriver.page_source.encode("utf-8")
		zhText = zhDriver.page_source.encode("utf-8")
		#print htmlText
		enFull = BeautifulSoup(enText)
		zhFull = BeautifulSoup(zhText)

		for i in range(len(chList)):
			print "loading {0}...".format(chList[i])
			findEnTitles = enFull.find_all("a", chList[i])
			findZhTitles = zhFull.find_all("a", chList[i])
			fullEnDay = [title.parent.parent for title in findEnTitles]
			fullZhDay = [title.parent.parent for title in findZhTitles]
			for e in range(len(fullEnDay)):
				print "parsing {0} out of {1} events...".format(e, len(fullEnDay))
				enTitle = fullEnDay[e].find("a",chList[i]).get_text()
				zhTitle = fullZhDay[e].find("a",chList[i]).get_text()
				print "loading English info..."
				enInfo = getLinkInfo(infoDriver, fullEnDay[e].find("a",chList[i]).get("href"))
				print "loading Chinese info..."
				zhInfo = getLinkInfo(infoDriver, fullZhDay[e].find("a",chList[i]).get("href"))
				time = fullEnDay[e].find("div", "font_content").get_text()
				schedule[chList[i]].append([url_date,time, enTitle, zhTitle,
								enInfo.encode("utf-8"), zhInfo.encode("utf-8")])
				#schedule[chList[i]].append([url_date,textTime(time), enTitle, zhTitle.encode("utf-8")])

def output(schedule, channel, start_date, end_date):
	startDate = re.findall(r'\d+',start_date)
	endDate = re.findall(r'\d+',end_date)
	file_name = "{0}_{1}-{2}.csv".format(channel, "{0}{1}{2}".format(startDate[0],
					startDate[1], startDate[2]), "{0}{1}{2}".format(endDate[0],
					endDate[1],endDate[2]))
	with open(file_name, "wb") as outputFile:
		csvWrite = csv.writer(outputFile)
		for i in schedule:
			csvWrite.writerow(i)
	
if __name__ == "__main__":
	tomorrow = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime("%Y/%m/%d")
	start = raw_input("Enter start date (i.e. '{0}'): ".format(tomorrow))
	end = raw_input("Enter end date (check availability first): ")
	scrape(dateStr(start), (dateStr(end)-dateStr(start)).days+1)

	output(hbo,"hbohd",start, end)
	output(signature,"signature",start,end)
	output(family, "family",start,end)
	output(hits,"hits",start,end)
	output(cinemax,"cinemax",start,end)
	