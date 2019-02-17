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

def get_dependencies():
	input = quote('flask') # https://docs.python.org/3/library/shlex.html#shlex.quote
	pip_show = subprocess.Popen(['pip', 'show', input], stdout=subprocess.PIPE)
	grep = subprocess.Popen(['grep', 'Requires'], stdin=pip_show.stdout,
	                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	pip_show.stdout.close() # Allow proc1 to receive a SIGPIPE if proc2 exits.
	out, err = grep.communicate()
	output = str(out).strip('b\'Requires:').strip('\\n').lstrip()
	split_result = output.split(', ')
	count = len(split_result)
	
	for i in range(count):
		print(split_result[i])
		# Jinja2
		# itsdangerous
		# click
		# Werkzeug


update_package_list()
#get_dependencies()