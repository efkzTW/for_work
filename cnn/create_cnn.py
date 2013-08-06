import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
#from selenium.webdriver.common.by import By
#from selenium.webdriver.support.wait import WebDriverWait
#from selenium.webdriver.support import expected_conditions as EC
from time import sleep

def load_online_data():

	tomorrow = (datetime.datetime.today() + datetime.timedelta(days=1)).date()
	url_base = "http://www.locatetv.com/listings/cnn-hd#"
	url_date = "{0}-{1}-{2}".format(tomorrow.strftime("%d"), tomorrow.strftime("%b"), tomorrow.year)

	driver = webdriver.PhantomJS("phantomjs")
	driver.get(url_base+url_date)
	
	#wanted_class = "{0} selected".format(tomorrow.strftime("%b").lower())
	#wanted_id = "C{0}-{1}-{2}".format(tomorrow.strftime("%d"), tomorrow.strftime("%b"), tomorrow.year)

	#wanted_div_selector = "//div[@class='{0}' and @id='{1}']".format(wanted_class,wanted_id)
	#print wanted_div_selector
	#WebDriverWait(driver, 10, 0.1).until(
	#	EC.presence_of_element_located((By.XPATH, wanted_div_selector))
	#)
	sleep(3)
	htmlText = driver.page_source.encode("utf-8")
	#print htmlText
	soup = BeautifulSoup(htmlText)

	results = soup.find_all('ul', 'schedule hoverable', id="S{0}".format(url_date))

	output_list = []

	for i in results:
		output_list.append(i.get_text())
	print output_list

if __name__ == "__main__":
	load_online_data()
