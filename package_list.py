import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import subprocess
from shlex import quote


def update_package_list():
	conn = sqlite3.connect('pypi_packages.db')

	c = conn.cursor()

	c.execute('''CREATE TABLE IF NOT EXISTS pypi 
				(id INTEGER PRIMARY KEY AUTOINCREMENT, package_name TEXT UNIQUE, date_added INTEGER, has_been_added INTEGER)''')

	r = requests.get('https://pypi.org/simple/')

	soup = BeautifulSoup(r.text, 'html.parser')

	for a_href in soup.find_all('a'):
		unixtime = int(time.time())
		package_name = a_href.get_text()

		c.execute("INSERT OR IGNORE INTO pypi (package_name, date_added) VALUES (?, ?)", (package_name, unixtime))

	print('Done updating DB')

	conn.commit()
	conn.close()

update_package_list()
