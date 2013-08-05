import sqlite3

with sqlite3.connect('cr1.db') as connection:
	c = connection.cursor()

	c.execute('''CREATE TABLE cr1_list( num INT,
					file_name TEXT, epg_title TEXT, title TEXT, actress TEXT, full_runtime TEXT,
					runtime INT, count INT, flag INT)''')

