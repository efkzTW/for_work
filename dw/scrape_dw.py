import datetime, re, sqlite3, io, json, os
from bs4 import BeautifulSoup
from selenium import webdriver

channel = "dw"
epg_channel = "DWAPS"
db_table = "{0}_programs".format(channel)
time_diff = 0

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

def dbSearchAdd(sch):
	complete_epg_data = []
	with sqlite3.connect("{0}.db".format(channel)) as connection:
		c = connection.cursor()
		rev_start = ""
		extra_time = ""
		prev_runtime = 0
	#add new program into db
		for i in range(len(sch)):
			#['m/d/yyyy', 'h:m', u'show title', u'language', u'some description']
			print sch[i]
			#current show date/time
			date = re.findall(r'\d+', sch[i][0])
			time = re.findall(r'\d+', sch[i][1])
			dt = datetime.datetime(int(date[2]),int(date[0]),int(date[1]),
						int(time[0]),int(time[1])) + datetime.timedelta(hours=time_diff)
			try:
				#next show date/time if exists
				date1 = re.findall(r'\d+', sch[i+1][0])
				time1 = re.findall(r'\d+', sch[i+1][1])
				dt1 = datetime.datetime(int(date1[2]),int(date1[0]),int(date1[1]),
						int(time1[0]),int(time1[1])) + datetime.timedelta(hours=time_diff)
			except IndexError:
				dt1 = datetime.datetime(int(date[2]),int(date[0]),int(date[1])+1,
							0,0) + datetime.timedelta(hours=time_diff)
				
			runtime = (dt1-dt).seconds/60

			#if runtime less than 5 min (minimum), do not add to schedule
			if runtime < 5:
				rev_start = dt # show start time will be set as next show's start time
				extra_time = runtime # runtime will be added onto next show's runtime
			else:
				if i > 0 and prev_runtime < 5: #if previous show had runtime of less than 5 min
					dt = rev_start # takeover that start time
					runtime += extra_time #add the removed runtime onto current runtime

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

			prev_runtime = runtime #assign so next show can check previous runtime

	return complete_epg_data

def dbAdd(c, newTitle):

	c.execute("SELECT MAX(show_num) FROM {0}".format(db_table))
	max_num = c.fetchone()[0]
	new_info = {"channel": "{0}{1}".format(epg_channel.upper(),"-E"), "event_type": "SH", "show_num": max_num + 1, 
			"ep_num": 0, "show_key": newTitle, "en_title": newTitle, "chi_title": newTitle, 
			"en_ep": u"", "chi_ep": newTitle, "en_desc": u"", "chi_desc": u"", "s_type": "NEW", "sub_type": u"",
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
	file_name = "{0}_{1}{2}{3}.json".format(channel,date.strftime('%m'), date.strftime('%d'), date.year)
	with io.open(file_name, "w", encoding="utf-8") as f:
		f.write(unicode(json.dumps(schedule)))

if __name__ == '__main__':
	schedule = load_url()
	complete_sch = dbSearchAdd(schedule)
	output_file(complete_sch)