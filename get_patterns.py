import pandas as pd
from Queue import Queue
import threading
import unicodecsv as csv
import requests
import json
import random

key = '2D434136F0BB4DCBA676'
secret = 'G+xQPG2VSpdh+N40Xuj4rY0rkSHb/LK2c35wdhTY'

personal = '3UWWOv8shFrGeQFQjqmVhBlEULCC8ahYwBTHk9eL'



def get_response(pattern_id):
	retries = 0
	url = "https://api.ravelry.com/patterns/%d.json" % pattern_id
	while retries < 3:
		try:
			response = requests.get(url, 
									auth=(key, personal),
									timeout=5)
			response.raise_for_status()
			return response
		except(requests.ConnectionError):
			print "Encountered error with pattern %d" % pattern_id
			retries += 5
		except(requests.exceptions.HTTPError):
			print "Error Encountered!"
			print response
			retries += 5
		except(requests.ReadTimeout):
			retries += 1
	return None
	
def parse_pattern(content_dict, pattern_id):
	try:
		attributes = ['permalink', 'difficulty_average', 'gauge_divisor', 'gauge', 'row_gauge', 'gauge_pattern', 'yardage']
		pattern_data = [pattern_id,
						'|'.join([att['permalink'] for att in content_dict['pattern']['pattern_attributes']]),
						'|'.join([att['permalink'] for att in content_dict['pattern']['pattern_categories']]),
						content_dict['pattern']['difficulty_average']]
		for attribute in attributes:
			pattern_data.append(content_dict['pattern'].get(attribute))
		ply = None
		if content_dict['pattern'].get('yarn_weight'):
			ply = content_dict['pattern']['yarn_weight']['ply']
		pattern_data.append(ply)
		pattern_data.append(content_dict['pattern']['craft']['permalink'])
		return pattern_data
	except(KeyError):
		return [pattern_id] + [None] * 12
	
def get_patterns(in_queue, out_queue):
	while True:
		if random.randint(0,25) == 24:
			print in_queue.qsize()
		pattern_id = in_queue.get()
		response = get_response(pattern_id)
		if response:
			content_dict = json.loads(response._content)
			pattern_data = parse_pattern(content_dict, pattern_id)
			out_queue.put(pattern_data)
		in_queue.task_done()
	
def write_pattern_data(pattern_data_queue, file_name):
	with open(file_name, 'a') as results_file:
		writer = csv.writer(results_file, encoding='utf-8')
		while True:
			pattern_data = pattern_data_queue.get()
			try:
				writer.writerow(pattern_data)
			except Exception, e:
				print ("Writer done fucked up, that's what: %s" % e)
			pattern_data_queue.task_done()

patterns_df = pd.read_csv('more_patterns.csv')
patterns = list(patterns_df['pattern_id'].astype('int'))

pattern_queue = Queue()
pattern_data_queue = Queue()

for i in range(75):
	worker = threading.Thread(target=get_patterns, args=(pattern_queue, pattern_data_queue))
	worker.setDaemon(True)
	worker.start()

for i in range(0, 5):
	file_name = 'pattern_data_%d.csv' % (i+1)
	file_writer = threading.Thread(target=write_pattern_data, args=(pattern_data_queue, file_name,))
	file_writer.setDaemon(True)
	file_writer.start()

for pattern in patterns:
	pattern_queue.put(pattern)

pattern_queue.join()
pattern_data_queue.join()

	
	

	
