import xlrd, sqlite3, sys, datetime
import romnum #custom script to convert int to roman numerals

def round_time(num):
	if num % 5 >= 3:
		num += 5 - (num % 5)
	elif num % 5 <= 2:
		num -= num % 5
	return num

def check_len(input):
	if len(str(input)) == 1:
		return '0' + str(input)
	else:
		return str(input)

def is_number(value):
	try:
		float(value)
		return True
	except ValueError:
		return False

def read_new(file_name):
	wb = xlrd.open_workbook(file_name)
	s = wb.sheet_by_index(0)
	full_sch = []
	for row in range(s.nrows):
		if row > 0:
			values = []
			n = 0
			for col in range(s.ncols):
				cell_value = s.cell(row,col).value
				if n == 3 and is_number(cell_value):
					time = xlrd.xldate_as_tuple(cell_value,1)
					dt = "{0}:{1}:{2}".format(check_len(time[3]),check_len(time[4]),check_len(time[5]))
					values.append(dt)
					cell_value = time[3]*60 + time[4]
				values.append(cell_value)
				n += 1
			full_sch.append(values)
	return full_sch

def load_db(data_list):
	with sqlite3.connect('cr1.db') as connection:
		c = connection.cursor()
		for each in data_list:
			epg_title = "Venus " + romnum.convert(int(each[0][-4:]))
			runtime = round_time(each[4])

			c.execute('''insert into cr1_list values (?,?,?,?,?,?,?,?,?)''',
					[int(each[0][-4:]),each[0], epg_title, each[1], each[2], each[3], runtime,
					each[5], each[6]])

if __name__ == '__main__':
	load_file = sys.argv[1]
	data = read_new(load_file)
	load_db(data)

