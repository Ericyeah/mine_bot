# A bot to automate the playing of satoshi mines

import time
import re
import csv
import random
import argparse 
from selenium import webdriver
from selenium.webdriver.common.by import By

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

global driver
global bankroll

global wealth_record 
global wins

def main(num_bombs, num_clicks, percent):
	print 'Begin'

	# set up global vars
	global driver
	global bankroll
	global wealth_record
	global wins
	driver = webdriver.Chrome() 
	bankroll = 25000
	wealth_record = [bankroll]
	wins = []

	# Go to satoshi mines
	print 'Going to satoshi mines...'
	driver.get('https://satoshimines.com/');

	# click start playing button
	driver.find_element(By.CLASS_NAME, 'primary_btn').click()
	# set mines to 1
	driver.find_element(By.XPATH, '//button[text()="{}"]'.format(num_bombs)).click()
	# start playing
	play(num_clicks, percent)

def play(num_clicks, percent):
	limit = 500
	i = 0

	while (i < limit):
		bet = set_bet(percent)
		# click play
		time.sleep(0.2)
		try_to_click(By.XPATH, '//button[text()="Play"]')

		time.sleep(0.175)
		round_res = click_buttons(num_clicks)

		# round over, get stats 
		winner = end_round(round_res)

		# cashout if win 
		if winner:
			try_to_click(By.XPATH, '//button[text()="Cashout"]')
		i += 1

	driver.quit()

# sets the bet for the round based on current bankroll 
# TODO: Set as cmdline arg
def set_bet(percent):
	max_bet = 1000000

	bet = (bankroll * percent)
	bet = round(bet,0)
	bet = int(bet)

	if bet >= max_bet:
		bet = max_bet

	bet_box = driver.find_element(By.CLASS_NAME, 'bet')
	bet_box.clear()
	bet_box.send_keys(bet)
	return bet

# prints win / loss info for each round 
# update statistics
def end_round(result):
	global bankroll
	global wins 
	global wealth_record

	bankroll += result
	winna = result > 0

	# winna!
	if winna:
		print bcolors.OKGREEN + 'Won ' + str(result)
		wins.append(True)
	# losa!
	else:
		print bcolors.FAIL + "Lost " + str(result)
		wins.append(False)

	print 'Total: ' + str(bankroll) + bcolors.ENDC
	wealth_record.append(bankroll)
	return winna

def check_click():
	global bankroll
 	win = False

 	time.sleep(0.2)
 	while 1:
	 	try:
			result = driver.find_element(By.CLASS_NAME, 'messages').find_element(By.CLASS_NAME, 'bomb').text
			break
	 	except Exception:
	 		try:
	 			result = driver.find_element(By.CLASS_NAME, 'messages').find_element(By.CLASS_NAME, 'find').text
	 			win = True
	 			break
	 		except Exception:
	 			pass

 	result = result.replace(',','')

 	if win:
 		swing = [int(s) for s in result.split() if s.isdigit()][0] 
 	else:
 		swing = [int(s) for s in result.split() if s.isdigit()][1] * -1

 	return swing

def click_buttons(num_clicks):
	guessed = []
	running_total = 0

	for i in xrange(num_clicks):

		rand = random.randint(1, 25)
		while rand in guessed:
			rand = random.randint(1, 25)
		guessed.append(rand)

		try_to_click(By.XPATH, '//ul[@class="board"]/li[{}]'.format(rand))

		last_click = check_click()
		if last_click < 0:
			running_total = last_click
			break
		else:
			running_total += last_click

	return running_total

# works around exceptions and time.sleep() by trying
# to get elements in a while loop
def try_to_click(by, desc):
	time.sleep(0.2)
	while 1:
		try:
			driver.find_element(by, desc).click()
			break
		except Exception:
			pass

def write_result():
	with open('mine_results.csv', 'wb') as res:
		wr = csv.writer(res, quoting=csv.QUOTE_ALL)
		wr.writerow(wins)
		wr.writerow(wealth_record)

if __name__ == "__main__": 
	# parse cmdline args 
	parser = argparse.ArgumentParser(description=
		'Arg1 = num_bombs: 1, 3, 5, or 24, Arg2 = num_clicks, Arg3 = percent to bet each round')
	parser.add_argument('integers', metavar='N', type=int, nargs='+')
	parser.add_argument('percent', type=float)
	args = parser.parse_args()

	main(args.integers[0], args.integers[1], args.percent)