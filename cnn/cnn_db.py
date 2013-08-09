import sqlite3, sys, csv, datetime

channel = 'cnn'

def create_db():
	with sqlite3.connect('{0}.db'.format(channel)) as connection:
		c = connection.cursor()

		c.execute('''CREATE TABLE {0}_programs(
					channel TEXT, event_type TEXT,show_num INT, ep_num INT,
					show_key TEXT, en_title TEXT, chi_title TEXT, en_ep TEXT,
					chi_ep TEXT, en_desc TEXT, chi_desc TEXT, s_type TEXT,
					sub_type TEXT, rating TEXT ,rating_exp_1 TEXT,
					rating_exp_2 TEXT, rating_exp_3 TEXT,
					rating_exp_4 TEXT, dolby_type TEXT, first_air_date TEXT,
					add_date TEXT) 
					'''.format(channel))

def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
	csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
	for row in csv_reader:
		yield[unicode(cell,'utf-8') for cell in row]

def import_data(source):
	with sqlite3.connect('{0}.db'.format(channel)) as connection:
		c = connection.cursor()
		show_info = unicode_csv_reader(open(source))

		for e in show_info:

			if e[0][-2:] != "-E":
				c.execute('''UPDATE {0}_programs SET chi_title = ?, chi_ep = ?, chi_desc = ? 
							WHERE show_num = ?'''.format(channel),
							(e[4], e[5], e[6], e[2]))
			else:
				today = datetime.datetime.today()
				s_today = "{0}-{1}-{2}".format(today.year, today.strftime("%m"), today.strftime("%d"))
				c.execute('''INSERT INTO {0}_programs (channel, event_type, show_num, ep_num,
							show_key, en_title, en_ep, en_desc, s_type, sub_type, rating,
							rating_exp_1, rating_exp_2, rating_exp_3, rating_exp_4, dolby_type, 
							first_air_date, add_date) 
							VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''.format(channel), 
									[e[0], e[1], e[2], e[3], e[4], e[4], e[5], e[6], e[7],
									e[8], e[9],e[10],e[11],e[12],e[13],e[14],e[15],s_today])

def clear_db():
	with sqlite3.connect('{0}.db'.format(channel)) as connection:
		c = connection.cursor()

		c.execute("DELETE * FROM {0}_programming".format(channel))

if __name__ == "__main__":

	command = raw_input("create/import/clear: ")
	
	if command == "create":
		create_db()
	elif command == "import":
		file_name = raw_input("file name: ")
		import_data(file_name)
	elif command == "clear":
		clear_db()