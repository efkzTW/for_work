import sqlite3, random, datetime, sys, json, os, io

def find_avg():
	with sqlite3.connect('cr1.db') as connection:
		c = connection.cursor()
		c.execute("select avg(count) from cr1_list where count > 0")
		avg = c.fetchone()
	return avg[0]

def show_count():
	with sqlite3.connect('cr1.db') as connection:
		c = connection.cursor()
		c.execute("select max(num) from cr1_list")
		max_num = c.fetchone()
	return max_num[0]

def select_random(show_total):
	with sqlite3.connect('cr1.db') as connection:
		c = connection.cursor()
		select = None
		while select == None:
			ran_num = random.randint(0,show_total)
			c.execute("select * from cr1_list where num = {0} and flag = 1".format(
						ran_num))
			select = c.fetchone()
	return select

def update_count(show_num):
	with sqlite3.connect('cr1.db') as connection:
		c = connection.cursor()
		c.execute("select count from cr1_list where num = {0}".format(show_num))
		add_one = c.fetchone()[0] + 1
		c.execute("update cr1_list set count = {0} where num = {1}".format(add_one, show_num))

def update_date(end_date):
	with sqlite3.connect('cr1.db') as connection:
		c = connection.cursor()
		c.execute("update others set last_date = '{0}'".format(end_date))

def find_min(text_time):
	#find minute from time string hh:mm:ss
	hour = int(text_time[:2])
	minute = int(text_time[3:5])
	if int(text_time[-2:]) > 29:
		minute += 1

	#print hour * 60 + minute
	return hour * 60 + minute

def create(show_total, days):
	selected = []
	complete_list = []
	playtime_limit = 615 #11am to 7am = 20 hours / repeat daily list once
	
	for day in range(days):
		day_list = []
		per_counts = []
		playtime = 0
		while playtime <= (playtime_limit - 50):
			show = select_random(show_total)
			avg = find_avg()
			if playtime + find_min(show[5]) < playtime_limit and show[1] not in selected:
				if len(day_list) == 0 or float(sum(per_counts))/len(per_counts) < avg:
					day_list.append(show)
					per_counts.append(show[7])
					selected.append(show[1])
					playtime += find_min(show[5]) #base it on full runtime
				else:
					if show[7] <= avg:
						day_list.append(show);
						per_counts.append(show[7])
						selected.append(show[1])
						playtime += find_min(show[5])

		for show in day_list:
			update_count(show[0])

		complete_list.append([day_list*2])
		#print day_list
	return complete_list

def check_len(input):
	if len(str(input)) == 1:
		return '0' + str(input)
	else:
		return str(input)

def add_datetime(playlist):
	with sqlite3.connect('cr1.db') as connection:
		#find last schedule date generated
		c = connection.cursor()
		c.execute("select last_date from others")
		d = c.fetchone()[0]
		last_date = datetime.date(int(d[:4]),int(d[5:7]),int(d[-2:]))

		c.execute("select * from cr1_list where num=0")
		slate = c.fetchone()

	#print slate	
	print "Enter Start Date:"
	reply = ''
	while reply == '' or reply not in 'yn':
		reply = raw_input("Is it {0}? (y/n): ".format(last_date))
	
	if reply.lower() == 'n':
		d = raw_input("Start date (yyyy-mm-dd): ")
		start = datetime.date(int(d[:4]),int(d[5:7]),int(d[-2:]))
	elif reply.lower() == 'y':
		start = last_date

	end = str(start + datetime.timedelta(days=len(playlist)))
	update_date(end) #update last scheduled date

	start_datetime = datetime.datetime(start.year, start.month, start.day, 11,0,0)
	
	file_date = "{0}-{1}-{2}".format(start_datetime.date().month,
								start_datetime.date().day, start_datetime.date().year)
	#start_time = start_datetime.time()
	complete_schedule = []
	day = 0
	while day < len(playlist):
		for i in range(len(playlist[day])):
			for each in range(len(playlist[day][i])):
				"""start show time adjustment"""
				output_time_0 = start_datetime
				minute_diff = output_time_0.time().minute % 5
				if minute_diff == 0:
					pass
				elif minute_diff >= 3:
				    output_time_0 += datetime.timedelta(minutes=(5-minute_diff))
				elif minute_diff < 3:
					output_time_0 -= datetime.timedelta(minutes=minute_diff)
				"""end here"""
				show_time = "{0}:{1}".format(check_len(output_time_0.time().hour),
												check_len(output_time_0.time().minute))
				show_date = "{0}/{1}/{2}".format(output_time_0.date().month,
								output_time_0.date().day, output_time_0.date().year)
				start_datetime += datetime.timedelta(hours=int(playlist[day][i][each][5][:2]), 
													minutes=int(playlist[day][i][each][5][3:5]),
													seconds=int(playlist[day][i][each][5][-2:]))
				print "start datetime: {0}".format(start_datetime)
				"""add output_time_1 to calculate actual runtime difference based on round-off"""
				output_time_1 = start_datetime
				#print output_time_1
				#print output_time_0
				seconds = (output_time_1 - output_time_0).seconds #difference in seconds
				minutes = seconds // 60
				if minutes % 5 == 0:
					pass
				elif minutes % 5 < 3:
					minutes -= minutes % 5
				elif minutes % 5 >= 3:
					minutes += 5 - minutes % 5
				
				show_runtime = minutes
				"""end"""
				
				print "output_0: {0}".format(output_time_0)
				channel = 'VENUS'
				event_type = 'MV'
				show_num = '0890' + playlist[day][i][each][1][-4:]
				ep_num = '0000'
				show_title = playlist[day][i][each][2]
				ep_title = playlist[day][i][each][4]
				show_desc = playlist[day][i][each][3]
				show_type = 'MOV'
				sub_type = ''
				rating = 'R'
				rating_1 = "Adult Content"
				rating_2 = "Strong Sexual Content"
				rating_3 = ''
				rating_4 = ''
				dolby = 'Dolby'
				air_date = ''

				complete_schedule.append([show_date, show_time, show_runtime, channel, event_type,
								show_num, ep_num, show_title, ep_title, show_desc, show_type,
								sub_type, rating, rating_1, rating_2, rating_3, rating_4,
								dolby, air_date])

		#adjust the time to be right on 5 minute interval with 0 seconds
		start_datetime = datetime.datetime(start_datetime.date().year,
											start_datetime.date().month,
											start_datetime.date().day,
											start_datetime.time().hour,
											start_datetime.time().minute,
											0)
		if start_datetime.time().minute % 5 == 0:
			pass
		elif start_datetime.time().minute % 5 >= 3:
			start_datetime += datetime.timedelta(minutes=5- start_datetime.time().minute % 5)
		elif start_datetime.time().minute % 5 < 3:
			start_datetime -= datetime.timedelta(minutes=start_datetime.time().minute % 5)

		break_1 = datetime.datetime(start_datetime.date().year, start_datetime.date().month,
							start_datetime.date().day, 9,0,0)
		#first break sessino ends at 9:00:00 AM
		#break_min = (break_1 - start_datetime).seconds//60

		breaks = {0: (break_1 - start_datetime).seconds//60, 1: 120}
		for i in range(2):

			show_time = "{0}:{1}".format(check_len(start_datetime.time().hour), check_len(start_datetime.time().minute))
			complete_schedule.append([show_date,show_time,breaks[i], channel, event_type, '08900000',
								ep_num, slate[2], slate[4], slate[3], show_type, sub_type, rating,
								rating_1, rating_2, rating_3, rating_4, dolby, air_date])
			start_datetime += datetime.timedelta(minutes=breaks[i])

		day += 1

	return complete_schedule, file_date

def search_time(show_num):
	with sqlite3.connect('cr1.db') as connection:
		c = connection.cursor()
		c.execute("select full_runtime from cr1_list where num = {0}".format(show_num))
		result = c.fetchone()[0]
		return result

def json_output(schedule, file_date):
	#print schedule[:3]
	file_name = "{0}_{1}.json".format("VENUS", file_date)
	txt_file = "{0}_{1}.txt".format("VENUS", file_date)
	script_dir = os.path.dirname(__file__)
	rel_path = "output/" + file_name
	rel_path2 = "output/" + txt_file
	with io.open(os.path.join(script_dir,rel_path), 'w',encoding='utf-8') as f:
		f.write(unicode(json.dumps(schedule)))

	with io.open(os.path.join(script_dir, rel_path2), 'w', encoding='utf-8') as f:
		#output to text file for playout system
		f.write("\t".join([unicode("No."), unicode("Date"), unicode("Start"), unicode('Runtime'),
							unicode("File"), unicode("EPG"), unicode("Movie"),unicode("Actress"),'\n']))
		showlist = ['0000']
		num = ''
		total_runtime = datetime.datetime(1800,1,1,0,0,0,0)
		for i in range(len(schedule)): 
			show_num = schedule[i][5][-4:]
			ft = search_time(show_num) #full_time
			summary = ''
			if show_num in showlist:
				num = ''
			elif num == '' and show_num not in showlist:
				showlist.append(show_num)
				num = 1
				total_runtime += datetime.timedelta(hours=int(ft[:2]), minutes = int(ft[3:5]), seconds = int(ft[-2:]))
			elif show_num not in showlist and schedule[i+1][5][-4:] in showlist:
				num += 1
				total_runtime += datetime.timedelta(hours=int(ft[:2]), minutes = int(ft[3:5]), seconds = int(ft[-2:]))
				showlist.append(show_num)
				if total_runtime.minute >= 0:
					summary = '\tTotal Runtime\t{0}:{1}:{2} ({3})'.format(check_len(total_runtime.hour), check_len(total_runtime.minute),
										check_len(total_runtime.second), num)
				total_runtime = datetime.datetime(1800,1,1,0,0,0,0)
			else:
				showlist.append(show_num)
				num += 1
				total_runtime += datetime.timedelta(hours=int(ft[:2]), minutes = int(ft[3:5]), seconds = int(ft[-2:]))

			info = "\t".join([unicode(num) + unicode("."), schedule[i][0], schedule[i][1], search_time(show_num), unicode("Venus-") + schedule[i][5][-4:], 
							schedule[i][7], schedule[i][9], schedule[i][8], summary, '\n'])
			f.write(info)


if __name__ == '__main__':
	days = 7
	count = show_count()
	full_list = create(count, days)
	full_sch, file_date = add_datetime(full_list)
	json_output(full_sch, file_date)