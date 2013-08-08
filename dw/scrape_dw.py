import datetime, csv, re
from bs4 import BeautifulSoup
from selenium import webdriver

def removeNonAscii(s):
	return "".join([x if ord(x) < 128 else '?' for x in s])

def load_url():
	#attempt to use Ghost.py to interact with javascript content
	url = "http://www.dw.de/program/tv-program-guide/s-4757-9801"
	driver = webdriver.PhantomJS("phantomjs")
	driver.get(url)
	htmlText = driver.page_source.encode("utf-8")
	#print htmlText

	full_html = BeautifulSoup(htmlText)

	full_schedule = []

	for d in range(1,7):
		daily_sch = BeautifulSoup("{0}".format(full_html.find('div',id="dif{0}".format(d))))

		#print daily_sch
		sch_date = daily_sch.find("th", id="currentDate").get_text()
		sch_time = daily_sch.find_all("td","time")
		sch_showInfo = daily_sch.find_all("div","bubLinkWrap")
		sch_lang = daily_sch.find_all("td", "lang")

		#find and filter date text
		re_date = filter(bool, re.findall(r'\d*',sch_date))
		date = "{0}/{1}/{2}".format(re_date[1],re_date[0],re_date[2])
		#there are two 'time' classes, and i need the even ones
		time_list = [sch_time[i].get_text() for i in range(len(sch_time)) if i % 2]
		title_list = [i.find("a").get_text() for i in sch_showInfo]
		info_list = [i.find("p").get_text().replace('\n','//')for i in sch_showInfo]
		lang_list = [i.get_text() for i in sch_lang]

		for i in range(len(time_list)):
			full_schedule.append([date, time_list[i], title_list[i], lang_list[i],
								info_list[i]])

	return full_schedule

def output_file(schedule):
	date = (datetime.datetime.today() + datetime.timedelta(days=1)).date()
	file_name = "DW_{0}{1}{2}.csv".format(date.strftime('%m'), date.strftime('%d'), date.year)
	with open(file_name, 'wb') as f:
		csvWrite = csv.writer(f)
		for i in schedule:
			if i[3] == "Deutsch":
				csvWrite.writerow([i[0],i[1],removeNonAscii(i[2]),i[3],""])
			else:
				csvWrite.writerow([i[0],i[1],removeNonAscii(i[2]),i[3],removeNonAscii(i[4])])

if __name__ == '__main__':
	schedule = load_url()
	output_file(schedule)