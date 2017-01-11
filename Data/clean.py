import sys
import csv
from datetime import datetime
from pprint import pprint 
# import pandas as pd






def addToKeyList(key,item,dictionary):
	if key in dictionary:
		dictionary[key] += [item]
	else:
		dictionary[key] = [item]	







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
				totalCost = float(price) * n * 100 - fee

				spreadID = (symbol,exp)

				addToKeyList(spreadID,(n,spec,strike,price,tDate,fee),options)



			else:
				exp = "NA"
				spec   = "NA"
				strike = "NA"
				totalCost = float(price) * n - fee				

				addToKeyList(symbol,(n,price,tDate,fee),stocks)
				

pprint(options)
pprint(stocks)


for expDate in options:
	print("\n")
	print(expDate[0])
	print(expDate[1])

	dateGroups = {}

	for contract in options[expDate]:
		addToKeyList(contract[4],contract,dateGroups)

	options[expDate] = dateGroups
	
print(options)

















