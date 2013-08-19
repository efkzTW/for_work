import datetime, sys, csv, sqlite3, re
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep

'''successfully scrapped a javasript site using selenium + phantomjs webdriver, then
	use beautifulsoup as html dom parser'''

#global variables
url_base = "http://www.locatetv.com/listings/cnn-hd#"
channel = "cnnus"
db_table = "cnn_programs"
time_diff = 12

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

	#url_base = "http://www.locatetv.com/listings/cnn-hd#"
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

def dbSearchAdd(sch):
	complete_epg_data = []
	with sqlite3.connect("{0}.db".format(channel)) as connection:
		c = connection.cursor()
	#add new program into db
		for i in range(len(sch)):
			#['m/d/yyyy', 'h:m', u'show title',u'some description']
			print sch[i]
			date = re.findall(r'\d+', sch[i][0])
			time = re.findall(r'\d+', sch[i][1])
			try:
				date1 = re.findall(r'\d+', sch[i+1][0])
				time1 = re.findall(r'\d+', sch[i+1][1])
				dt = datetime.datetime(int(date[2]),int(date[0]),int(date[1]),
						int(time[0]),int(time[1])) + datetime.timedelta(hours=time_diff)
				dt1 = datetime.datetime(int(date1[2]),int(date1[0]),int(date1[1]),
						int(time1[0]),int(time1[1])) + datetime.timedelta(hours=time_diff)
				runtime = (dt1-dt).seconds/60
			except IndexError:
				dt = datetime.datetime(int(date[2]),int(date[0]),int(date[1]),
							int(time[0]),int(time[1])) + datetime.timedelta(hours=time_diff)
				dt1 = datetime.datetime(int(date[2]),int(date[0]),int(date[1])+1,
							0,0) + datetime.timedelta(hours=time_diff)
				runtime = (dt1-dt).seconds/60

			c.execute("SELECT * FROM {0} WHERE show_key = ?".format(db_table), [sch[i][2]])
			r = c.fetchone() #result
			remove = re.compile("-E")
			if r:
				print "found show"
				#english data
				complete_epg_data.append([dt.strftime("%d/%m/%Y"), dt.strftime("%H:%M"), runtime, 
								r[0], r[1], r[2], r[3], r[5], r[7], r[9], r[11], r[12], r[13],
								r[14], r[15], r[16], r[17], r[18], r[19]])
				#chinese data
				complete_epg_data.append([dt.strftime("%d/%m/%Y"), dt.strftime("%H:%M"), runtime, 
								remove.sub("",r[0]), 
								r[1], r[2], r[3], r[6], r[8], r[10], r[11], r[12], r[13],
								r[14], r[15], r[16], r[17], r[18], r[19]])
			else:
				print "adding..."
				eng_data, chi_data = dbAdd(c, schedule[i][2])
				for entry in [eng_data, chi_data]:
					data = [dt.strftime("%m/%d/%Y"), dt.strftime("%H:%M"), runtime]
					for i in range(len(entry)):
						if entry == chi_data and i == 0:
							data.append(remove.sub("",entry[i]))
						else:
							data.append(entry[i])
				complete_epg_data.append(data)

	print complete_epg_data
	print len(complete_epg_data)
	#print cInfo["show_num"]

def dbAdd(c, newTitle):

	c.execute("SELECT MAX(show_num) FROM {0}".format(db_table))
	max_num = c.fetchone()[0]
	new_info = {"channel": "{0}{1}".format(channel.upper(),"-E"), "event_type": "SH", "show_num": max_num + 1, 
			"ep_num": 0, "show_key": newTitle, "en_title": newTitle, "chi_title": newTitle, 
			"en_ep": u"", "chi_ep": u"", "en_desc": u"", "chi_desc": u"", "s_type": "NEW", "sub_type": u"",
			"rating": "G", "rating_exp_1": u"", 
			"rating_exp_2": u"", "rating_exp_3": u"", "rating_exp_4": u"", "dolby_type": "Dolby", 
			"first_air_date": str(datetime.datetime.today().date()), "add_date": str(datetime.datetime.today())
		}
	c.execute("INSERT INTO {0} VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)".format(db_table), (
				new_info["channel"], new_info["event_type"], new_info["show_num"], new_info["ep_num"],
				new_info["show_key"], new_info["en_title"], new_info["chi_title"], new_info["en_ep"],
				new_info["chi_ep"], new_info["en_desc"], new_info["chi_desc"], new_info["s_type"],
				new_info["sub_type"], new_info["rating"], new_info["rating_exp_1"],
				new_info["rating_exp_2"],new_info["rating_exp_3"], new_info["rating_exp_4"],
				new_info["dolby_type"], new_info["first_air_date"], new_info["add_date"]))

	eng_order = {0:"channel", 1:"event_type", 2: "show_num", 3: "ep_num", 4: "en_title", 5:"en_ep",
				6:"en_desc", 7:"s_type", 8:"sub_type", 9:"rating", 10:"rating_exp_1", 11:"rating_exp_2",
				12:"rating_exp_3", 13:"rating_exp_4", 14:"dolby_type", 15:"first_air_date"}
	chi_order = {0:"channel", 1:"event_type", 2: "show_num", 3: "ep_num", 4: "chi_title", 5:"chi_ep",
				6:"chi_desc", 7:"s_type", 8:"sub_type", 9:"rating", 10:"rating_exp_1", 11:"rating_exp_2",
				12:"rating_exp_3", 13:"rating_exp_4", 14:"dolby_type", 15:"first_air_date"}

	eng_new = [new_info[eng_order[i]] for i in range(16)]
	chi_new = [new_info[chi_order[i]] for i in range(16)]

	return eng_new, chi_new
		
def output_file(schedule):
	date = (datetime.datetime.today() + datetime.timedelta(days=1)).date()
	file_name = "{0}_{1}{2}{3}.csv".format(channel,date.strftime('%m'), date.strftime('%d'), date.year)
	with open(file_name, 'wb') as f:
		csvWrite = csv.writer(f)
		for i in schedule:
			csvWrite.writerow([i[0],i[1],i[2],i[3]])


if __name__ == "__main__":
	days = 9 #number of days out the website seems to provide
	schedule = load_online_data(days)
	dbSearchAdd(schedule)
	output_file(schedule)
