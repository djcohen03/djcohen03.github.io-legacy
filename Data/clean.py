import sys
import csv
from datetime import datetime
from pprint import pprint 
# import pandas as pd
import time
import HTML

import classes as c









def addToKeyList(key,item,dictionary):
	if key in dictionary:
		dictionary[key] += [item]
	else:
		dictionary[key] = [item]	


def addToTradeList(spreadID,trade,allSpreads):
	if spreadID not in allSpreads:
		allSpreads[spreadID] = [trade]
	else:
		for loggedTrade in allSpreads[spreadID]:
			if trade.contract.equals(loggedTrade.contract):
				# combine equivalent contracts:
				loggedTrade.n += trade.n
				loggedTrade.fee += trade.fee
				loggedTrade.price = ((trade.n * trade.contract.price) + (loggedTrade.n * loggedTrade.contract.price))/(loggedTrade.n + trade.n)
				return		
		allSpreads[spreadID] += [trade]





def identify_spread(option_list):
	n = len(option_list)
		
	if type(option_list[0]).__name__ == "StockTrade":
		return(option_list[0])


	if n == 1:
		return(option_list[0])
	
	if n == 2:
		c1 = option_list[0].contract
		c2 = option_list[1].contract
		t1 = option_list[0]
		t2 = option_list[1]

		eqstrikes = (c1.strike == c2.strike)
		eqtypes   = (c1.contract_type == c2.contract_type)
		eqquant   = (t1.n == t2.n)
		eqexpir	  = (c1.expiration == c2.expiration)

		if not eqexpir and eqstrikes:
			return(c.CalandarSpread(option_list))

		if not eqstrikes:
			return(c.VerticalSpread(option_list))
		else:
			return("Unknown")


	if n%4 == 0:
		return(c.IronCondor(option_list))

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

trades = {}


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
		if len(contract) > 1:	# i.e. most to specify than just symbol (expiration, strike, etc.)
			option = True




		# get symbol:
		symbol = contract[0]
		if symbol == "RUTW":
			symbol = "RUT"

		
		if info[0] == "Bought" or info[0] == "Sold":
			
			# get trade date
			tDate = datetime.strptime(row[0], "%m/%d/%y").date()

			# get trade price
			price = float(row[5])

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
				strike = float(contract[-2])

				option = c.Option(symbol,strike,exp,spec, price)
				trade = c.OptionsTrade(option,n,tDate)

				spreadID = (symbol,tDate,"option")
				addToTradeList(spreadID,trade,trades)

			else:
				
				stock = c.Stock(symbol,price)
				trade = c.StockTrade(stock,n,tDate)
				tradeID = (symbol,tDate,"stock")

				addToTradeList(tradeID,trade,trades)
				




trade_list = []
condors = []
for tradegroup in trades:
	trade_list += [trades[tradegroup]]


trade_list = sorted(trade_list, key = lambda x: int(time.mktime(x[0].tradedate.timetuple())))

for i in range(len(trade_list)):
	trade_list[i] = identify_spread(trade_list[i])

for i in range(len(trade_list)):
	for j in range(i):
		if trade_list[i].sameContract(trade_list[j]) and trade_list[j].openTrade and trade_list[i].openTrade:
			trade_list[j].addTrade(trade_list[i])
			trade_list[i].openTrade = False
						

for i in range(len(trade_list)):
	if type(trade_list[i]).__name__ != "StockTrade":
		if trade_list[i].isExpired():
			trade_list[i].expired()



historical = []

for i in range(len(trade_list)):
	if not trade_list[i].openTrade: 
		if trade_list[i].pnl != 0:
			historical.append(trade_list[i])



header = c.ClosedTrade(historical[0]).attrList()
closed_trades = []
for i in range(len(historical)):
	closed_trades.append(c.ClosedTrade(historical[i]).toList())
	
		


closed_trades.reverse()
	
			
htmltablecode = HTML.table(closed_trades, header_row=header, 
										  width = '60%',
										  col_align = ['left','left','left','left','left','left','center'],
										  col_styles=['font-weight: bold','','','','','',''],
										  col_classes = ['','','','','','','pnl'])
with open("htmlTable.txt", "w") as text_file:
    text_file.write(htmltablecode)




