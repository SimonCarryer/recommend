import pandas as pd
from Queue import Queue
import threading
import csv
import requests
import json
import random

key = '2D434136F0BB4DCBA676'
secret = 'G+xQPG2VSpdh+N40Xuj4rY0rkSHb/LK2c35wdhTY'

personal = '3UWWOv8shFrGeQFQjqmVhBlEULCC8ahYwBTHk9eL'



def get_response(user, page):
	retries = 0
	url = "https://api.ravelry.com/people/%s/favorites/list.json" % user
	while retries < 3:
		try:
			response = requests.get(url, 
									auth=(key, personal), 
									params={'page_size': 100, 'types':'pattern', 'page': page},
									timeout=5)
			response.raise_for_status()
			return response
		except(requests.ConnectionError):
			print "Encountered error with user %s" % user
			retries += 5
		except(requests.exceptions.HTTPError):
			print "400 Error Encountered!"
			print response._content
			retries += 5
		except(requests.ReadTimeout):
			retries += 1
	return None
	
def get_faves(in_queue, out_queue):
	while True:
		if random.randint(0,50) == 49:
			print in_queue.qsize()
		user = in_queue.get()
		faves = []
		response = get_response(user, 1)
		if response:
			content_dict = json.loads(response._content)
			faves += content_dict['favorites']
			page = content_dict['paginator']['page']
			last_page = content_dict['paginator']['last_page']
			if len(faves) > 0:
				while page <= last_page:
					page += 1
					response = get_response(user, page)
					if response:
						content_dict = json.loads(response._content)
						faves += content_dict['favorites']
						page = content_dict['paginator']['page']
				work = [[user, fave['favorited']['id'], fave['created_at']] for fave in faves]
				out_queue.put(work)
		in_queue.task_done()
	
def write_faves(faves_queue, file_name):
	with open(file_name, 'a') as results_file:
		writer = csv.writer(results_file)
		while True:
			faves = faves_queue.get()
			for row in faves:
				writer.writerow(row)
			faves_queue.task_done()

dones = []
for filename in ['user_faves_abc.csv', 'user_faves_abc_1.csv', 'user_faves_abc_2.csv', 'user_faves_abc_3.csv']:
	dones.append(pd.read_csv(filename, header = None, usecols=[0]))
done_files = pd.concat(dones)
done = set(done_files[0].unique())
print "Currently fetched faves for %d users." % len(done)
all_users = set(pd.read_csv('user_names_abc.csv')['user_name'])
users = list(all_users - done)

user_queue = Queue()
faves = Queue()

for i in range(100):
	worker = threading.Thread(target=get_faves, args=(user_queue, faves))
	worker.setDaemon(True)
	worker.start()

for i in range(4, 10):
	file_name = 'user_faves_abc_%d.csv' % (i+1)
	file_writer = threading.Thread(target=write_faves, args=(faves, file_name,))
	file_writer.setDaemon(True)
	file_writer.start()

for user in users[0:10000]:
	user_queue.put(user)

user_queue.join()
faves.join()

	
	

	
	