# A bot to automate the playing of satoshi mines

import time
import re
import csv
import random
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

def main():
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
	numbombs = 1

	# Go to satoshi mines
	print 'Going to satoshi mines...'
	driver.get('https://satoshimines.com/');

	# click start playing button
	driver.find_element(By.CLASS_NAME, 'primary_btn').click()
	# set mines to 1
	driver.find_element(By.XPATH, '//button[text()="{}"]'.format(numbombs)).click()
	# start playing
	play()

def play():
	limit = 300
	i = 0

	while(i < limit):
		bet = set_bet()
		# click play
		driver.find_element(By.XPATH, '//button[text()="Play"]').click()

		click_buttons()

		# round over, get stats 
		time.sleep(0.55)
		winner = end_round(bet)

		# cashout if win 
		if winner:
			try:
				driver.find_element(By.XPATH, '//button[text()="Cashout"]').click()
			except Exception:
				time.sleep(0.5)
				driver.find_element(By.XPATH, '//button[text()="Cashout"]').click()
		i += 1

	driver.quit()

# prints win / loss info for each round 
# update statistics
# return true if winner, false if loser 
def end_round(winner):
	global bankroll
	global wins 
	global wealth_record

	# We lost :(
 	try:
	 	loser = driver.find_element(By.CLASS_NAME, 'messages').find_element(By.CLASS_NAME, 'bomb').text
	 	loser = loser.replace(',','')
	 	losings = [int(s) for s in loser.split() if s.isdigit()][1]
	 	print bcolors.FAIL + "Lost " + str(losings)

	 	bankroll = bankroll - losings
	 	wealth_record.append(bankroll)
	 	print 'Total: ' + str(bankroll) + bcolors.ENDC
	 	wins.append(False)
	 	return False 

 	# We won :)
 	except Exception:
 		winner = driver.find_element(By.CLASS_NAME, 'messages').find_element(By.CLASS_NAME, 'find').text
 		winner = winner.replace(',','')
 		winnings = [int(s) for s in winner.split() if s.isdigit()][0]
 		print bcolors.OKGREEN + 'Won ' + str(winnings) 

 		bankroll = bankroll + winnings
 		wealth_record.append(bankroll)
 		print 'Total: ' + str(bankroll) + bcolors.ENDC
 		wins.append(True)
 		return True 

def check_click():
	global bankroll

 	win = False
 	try:
		result = driver.find_element(By.CLASS_NAME, 'messages').find_element(By.CLASS_NAME, 'bomb').text
 	except Exception:
 		result = driver.find_element(By.CLASS_NAME, 'messages').find_element(By.CLASS_NAME, 'find').text
 		win = True

 	result = result.replace(',','')

 	if not win:
 		swing = [int(s) for s in result.split() if s.isdigit()][1] * -1
 	else:
 		swing = [int(s) for s in winner.split() if s.isdigit()][0]

 	bankroll = bankroll + swing

 	return swing

# sets the bet for the round based on current bankroll 
# TODO: Set as cmdline arg
def set_bet():
	max_bet = 1000000
	percent = 0.1

	bet = (bankroll * percent)
	bet = round(bet,0)
	bet = int(bet)

	if bet >= max_bet:
		bet = max_bet

	bet_box = driver.find_element(By.CLASS_NAME, 'bet')
	bet_box.clear()
	bet_box.send_keys(bet)
	return bet

def click_buttons():
	to_click = 5
	guessed = []

	for i in range(to_click):

		rand = random.randint(1, 25)
		while rand in guessed:
			rand = random.randint(1, 25)
		guessed.append(rand)

		time.sleep(0.35)
		try:
			driver.find_element(By.XPATH, '//ul[@class="board"]/li[{}]'.format(rand)).click()

		except Exception:
			time.sleep(0.8)
			driver.find_element(By.XPATH, '//ul[@class="board"]/li[{}]'.format(rand)).click()

		#last_click = check_click()
		#if last_click < 0:
		#	break

	#end_round(last_click > 0)

def write_result():
	with open('mine_results.csv', 'wb') as res:
		wr = csv.writer(res, quoting=csv.QUOTE_ALL)
		wr.writerow(wins)
		wr.writerow(wealth_record)

if __name__ == "__main__": 
	main()