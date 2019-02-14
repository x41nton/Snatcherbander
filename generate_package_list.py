#!/usr/bin/python3
# https://python-forum.io/Thread-how-to-get-a-full-list-of-pypi-packages?pid=4919#pid4919

import json
import xmlrpclib
from collections import defaultdict
import time

class GetPyPi:
  def __init__(self):
    self.use_pkg_file = False
    self.packages = defaultdict(lambda: defaultdict(list))
    self.pkg_filename = 'packages.json'
    self.json_name = None
    self.client = xmlrpclib.ServerProxy('https://pypi.python.org/pypi')

  def try_package_release(self):
    allpackages = None
    print('updating package list')
    if self.use_pkg_file:
      with open(self.pkg_filename, 'r') as f:
        j = f.read()
        allpackages = json.loads(j)
    else:
      allpackages = self.client.list_packages()
      allpackages.sort()
      with open(self.pkg_filename, 'w') as f:
        j = json.dumps(allpackages)
        f.write(j)
    for n, item in enumerate(allpackages):
      print('Fetching release data for: {}'.format(item))
      releases = self.client.package_releases(item)
      for release in releases:
        time.sleep(.2)
        release_data = self.client.release_data(item, release)
        print('release_data: {}'.format(release_data))

if __name__ == '__main__':
  gpp = GetPyPi()
  gpp.try_package_release()
