from bs4 import BeautifulSoup
import requests
from typing import List
import csv

FULL_MARA_ID = 1
HALF_MARA1_ID = 2
HALF_MARA2_ID = 3

def fetch_page(event: str, race: int, start: int):
	params = {
		'do': 'race:results:oneclick',
		'EVID': event,
		'RCID': str(race),
		'SROW': str(start),
		'TYPE': 'overall'
	}
	return requests.get('https://www.runraceresults.com/Secure/raceResultsAPI.cfm', params=params)

def parse_results(res: str) -> List[List[str]]: 
	soup = BeautifulSoup(res, 'html.parser')
	tables = soup.find_all('table')
	if len(tables) != 2:
		import pdb; pdb.set_trace()
		raise Exception('Invalid format')
	res_table = tables[1]
	rows = res_table.find_all('tr')
	datarows = rows[1:]
	if len(datarows) == 0:
		return []
	data = [[dat.text for dat in row.find_all('td')] for row in datarows ]
	return data

def write_to_csv(data: List[List[str]], fname: str) -> None:
	with open(fname, 'w') as csvfile:
	    spamwriter = csv.writer(csvfile)
	    for row in data:
	    	spamwriter.writerow(row)

def read_csv(fname: str) -> List[List[str]]:
	data = []
	with open(fname, 'r') as csvfile:
	    spamreader = csv.reader(csvfile)
	    for row in spamreader:
	    	data.append(row)
	return data

def retrieve_race(event: str, race: int):
	start = True
	cur_data = []
	start_ix = 1
	data = []
	while start or len(cur_data) != 0:
		start = False
		print(f'Requesting with ix {start_ix}')
		resp = fetch_page(event, race, start_ix)
		cur_data = parse_results(resp.text)
		data += cur_data
		print(f'Retrieved: {len(cur_data)} Total: {len(data)}')
		start_ix = len(data) + 1
	return data

def one_off_merge(fname: str):
	first = read_csv('first_half_2021.csv')
	first = [['first'] + f for f in first]
	second = read_csv('second_half_2021.csv')
	second = [['second'] + s for s in second]
	combined = first + second 
	# sort by time
	combined.sort(key = lambda x : x[5])
	combined = [[str(i+1)] + x for i, x in enumerate(combined)]
	header = ['Place', 'Race', 'Race Place', 'Name', 'Location', 'Bib', 'Net Time', 'Pace', 'Division/Place', 'Sex-Age', 'Sex-Place', 'Gun Time', 'Age Grade']
	combined = [header] + combined
	write_to_csv(combined, fname)

if __name__ == '__main__':
	for event in range(2008, 2019):
		eventid = f'RCLF{event}'
		res = retrieve_race(eventid, HALF_MARA1_ID)
		write_to_csv(res, f'first_half_{event}.csv')


		res = retrieve_race(eventid, HALF_MARA2_ID)
		write_to_csv(res, f'second_half_{event}.csv')


		res = retrieve_race(eventid, FULL_MARA_ID)
		write_to_csv(res, f'full_{event}.csv')

	# res = retrieve_race(HALF_MARA1_ID)
	# write_to_csv(res, 'first_half_2021.csv')

	# res = retrieve_race(HALF_MARA2_ID)
	# write_to_csv(res, 'second_half_2021.csv')
	# # Merges the two half marathons
	# one_off_merge('half_2021.csv')

	# res = retrieve_race(FULL_MARA_ID)
	# write_to_csv(res, 'full_2021.csv')

