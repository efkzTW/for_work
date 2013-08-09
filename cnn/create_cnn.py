import datetime, sys, csv
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep

'''successfully scrapped a javasript site using selenium + phantomjs webdriver, then
	use beautifulsoup as html dom parser'''

def textTime(textTime):
	#convert show time on the website
	pos = textTime.index(":")
	hour, minute, ampm = int(textTime[:pos]), textTime[-4:-2], textTime[-2:]
	adjust = 0
	if ampm.lower() == "am" and hour == 12:
		adjust = -12
	elif ampm.lower() == "pm" and hour == 12:
		adjust = 0
	elif ampm.lower() == "pm":
		adjust = 12

	return "{0}:{1}".format(hour+adjust, minute)

def load_online_data(future_days):

	url_base = "http://www.locatetv.com/listings/cnn-hd#"
	schedule_list = []
	for d in range(1,future_days+1):
		driver = webdriver.PhantomJS("phantomjs")
		target_date = (datetime.datetime.today() + datetime.timedelta(days=d)).date()
		textDate = "{0}/{1}/{2}".format(target_date.month, target_date.day, target_date.year)
		#print target_date, textDate
		url_date = "{0}-{1}-{2}".format(target_date.strftime("%d"), target_date.strftime("%b"), target_date.year)
		driver.get(url_base+url_date)

		sleep(3)
		#print url_base+url_date
		htmlText = driver.page_source.encode("utf-8")
		#print htmlText
		full_html = BeautifulSoup(htmlText)

		#find the day schedule section in the entire html markup. id marks the schedule for the day
		search_schedule = full_html.find('ul', 'schedule hoverable', id="S{0}".format(url_date))
		#print search_schedule
		schedule = BeautifulSoup("{0}".format(search_schedule))

		schedule_time = schedule.find_all('li', 'time')
		schedule_title = schedule.find_all('li', 'title withPackshot')

		if len(schedule_time) == len(schedule_title):
			
			for i in range(len(schedule_title)):
				show = BeautifulSoup("{0}".format(schedule_title[i]))
				find_info = show.find_all('a','pickable')
				if show.find('p') != None:
					#sometimes longer description will exist in p
					description = show.find('p').get_text()

				if len(find_info) == 2:
					title = find_info[0].get_text()
					description = find_info[1].get_text()
					schedule_list.append([textDate,textTime(schedule_time[i].get_text()),title,description])
				elif len(find_info) == 1:
					title = find_info[0].get_text()
					schedule_list.append([textDate,textTime(schedule_time[i].get_text()),title,description])

		else:
			print "Double check: schedule count mismatch."
			sys.exit(0)

	return schedule_list
		
def output_file(schedule):
	date = (datetime.datetime.today() + datetime.timedelta(days=1)).date()
	file_name = "cnn_{0}{1}{2}.csv".format(date.strftime('%m'), date.strftime('%d'), date.year)
	with open(file_name, 'wb') as f:
		csvWrite = csv.writer(f)
		for i in schedule:
			csvWrite.writerow([i[0],i[1],i[2],i[3]])


if __name__ == "__main__":
	days = 9 #number of days out the website seems to provide
	schedule = load_online_data(days)
	output_file(schedule)
