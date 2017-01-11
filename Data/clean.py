import sys
import csv
from datetime import datetime
from pprint import pprint 
# import pandas as pd
import time
import HTML






def addToKeyList(key,item,dictionary):
	if key in dictionary:
		dictionary[key] += [item]
	else:
		dictionary[key] = [item]	





def addToSpreadList(spreadID,option,allSpreads):
	if spreadID not in allSpreads:
		allSpreads[spreadID] = [option]
	else:
		for contract in allSpreads[spreadID]:
			b1 = option['exp'] 	  	 == contract['exp']
			b2 = option['strike'] 	 == contract['strike']
			b3 = option['sym'] 	  	 == contract['sym']
			b4 = option['tradedate'] == contract['tradedate']
			b5 = option['type'] 	 == contract['type']
			if b1 & b2 & b3 & b4 & b5:
				# need to combine two fills for same contract
				comb = {'exp': option['exp'],
						'fee': option['fee'] + contract['fee'],
						'n': option['n'] + contract['n'],
						'price': (option['price']*option['n'] + contract['price']*contract['n'])/(option['n'] + contract['n']),
						'strike': option['strike'],
						'sym': option['sym'],
						'tradedate': option['tradedate'],
						'type': option['type']}

				allSpreads[spreadID].remove(contract)
				allSpreads[spreadID] += [comb]
				return
		allSpreads[spreadID] += [option]





def identify_spread(option_list):
	n = len(option_list)
	if option_list[0]["exp"] == "NA":
		return("Stock")

	else:
		if n == 1:
			return("Single")
		
		if n == 2:
			o1 = option_list[0]
			o2 = option_list[1]
			eqstrikes = (o1["strike"] == o2["strike"])
			eqtypes   = (o1["type"] == o2["type"])
			eqquant   = (o1["n"] == o2["n"])
			eqstrikes = (o1["strike"] == o2["strike"])
			eqexpir	  = (o1["exp"] == o2["exp"])

			if not eqexpir and eqstrikes:
				return("Calandar Spread")

			if not eqstrikes:
				if eqtypes:
					if o1["type"] == "Call":
						if o1["n"] > o2["n"]:
							if o1["strike"] < o2["strike"]:
								return("Bull Call Spread")
							else:
								return("Bear Call Spread")
						else: 
							if o1["strike"] > o2["strike"]:
								return("Bull Call Spread")
							else:
								return("Bear Call Spread")
					else:
						if o1["n"] > o2["n"]:
							if o1["strike"] < o2["strike"]:
								return("Bull Put Spread")
							else:
								return("Bear Put Spread")
						else: 
							if o1["strike"] > o2["strike"]:
								return("Bull Put Spread")
							else:
								return("Bear Put Spread")			
			else:
				return("Unknown")


		if n%4 == 0:
			return("Iron Condor")

		return("Unknown")





def spreadSummary(spread):
	stype = spread["type"]

	o1 = spread["options"][0]

	# universals
	symbol = o1["sym"]
	datePlaced = o1["tradedate"]
	n = o1["n"]
	if o1["exp"] != "NA":
		exp = o1["exp"].strftime("%b %d, %Y")
	else:
		exp = "NA"
		# additives
		fee = 0
		cost = 0
		price = 0
		n = 0
		for stock in spread["options"]:
			fee += stock["fee"]
			price += stock["price"]
			cost += price*stock["n"]
			n += stock["n"]
		fee = round(fee,2)
		price = round(price/len(spread["options"]),2)
		cost = round(cost,2)
		return([symbol,stype,n,datePlaced,exp,price,cost,fee])

	

	# additives
	fee = 0
	cost = 0
	price = 0
	for option in spread["options"]:
		price += option["price"]
		fee += option["fee"]
		cost += price*option["n"]*100

	fee = round(fee,2)
	price = round(price,2)
	cost = round(cost,2)
	return([symbol,stype,n,datePlaced,exp,price,cost,fee])












# Trades = pd.DataFrame(index = ['Symbol','N','Type','Strike','Exp','Price','Trade Date','Fee','Total Cost'])

options = {}
stocks  = {}


with open('transactions.csv', 'r') as csvreadfile:
	csvReader = csv.reader(csvreadfile, delimiter=',')
	
	i = 0
	tradeID = 0
	for row in csvReader:

		
		tid  		= row[1] 	# broker-specific trade id
		description = row[2]
		contract  	= row[4].split(" ")
		info 		= description.split(" ")


		# Check if the trade was an option contract
		option = False	
		if len(contract) > 1:
			option = True


		
		if info[0] == "Bought" or info[0] == "Sold":
			
			# get trade date
			tDate = datetime.strptime(row[0], "%m/%d/%y").date()

			# get trade price
			price = float(row[5])

			# get symbol:
			symbol = contract[0]
			if symbol == "RUTW":
				symbol = "RUT"



			# get trade quantity
			if info[0] == "Sold":
				n = -int(row[3])
			else: 
				n = int(row[3])

			# get trade fees:
			try:
				fee = float(row[6]) + float(row[9])
			except ValueError:
				fee = float(row[6])
			
			
			if option:
				exp    = datetime.strptime("/".join(contract[1:4]), "%b/%d/%Y").date()
				spec   = contract[-1]
				strike = float(contract[4])

				spreadID = (symbol,tDate)

				addToSpreadList(spreadID,{"sym":symbol,"n":n,"type":spec,"strike":strike,"price":price,"exp":exp,"tradedate":tDate,"fee":fee},options)



			else:
				exp = "NA"
				spec   = "NA"
				strike = "NA"
				tradeID = (symbol,tDate)

				addToKeyList(tradeID,{"sym":symbol,"n":n,"price":price,"tradedate":tDate,"fee":fee,"exp":exp,"strike":"NA"},options)
				

	

allTrades = []
for k in options:
	allTrades += [spreadSummary({"type":identify_spread(options[k]),"options":options[k]})]




allTrades = sorted(allTrades, key = lambda x: int(time.mktime(x[3].timetuple())))
allTrades.reverse()
for trade in allTrades:
	trade[3] = trade[3].strftime("%b %d, %Y")
	# print(trade)


			
htmltablecode = HTML.table(allTrades, header_row=["Symbol", 'Type', 'N', 'Date Placed', 'Expiration','Price', 'Cost', 'Fee'], width = '100%')

with open("htmlTable.txt", "w") as text_file:
    text_file.write(htmltablecode)






for trade in allTrades:
	prev = True
	for prevTrade in allTrades:
		if trade == prevTrade:
			prev = False


		if prev:
			# searching previous trades for opening
			b1 = trade[0] == prevTrade[0]		# same symbol
			b2 = trade[1] == prevTrade[1]		# same spread
			b3 = trade[2] == -prevTrade[2]		# same quantity n
			b4 = trade[4] == prevTrade[4]		# same expiration/both "NA"
			# b5 = trade[1] != "Stock"
			b5 = True

			if b1 & b2 & b3 & b4 & b5:
				print("\n\nOpen:")
				print(prevTrade)
				print("Close:")
				print(trade)
				print("PNL:")
				print(-(prevTrade[5] + trade[5]) - (trade[6] + prevTrade[6]))
				break
		else:
			# searching  trades for opening
			pass














