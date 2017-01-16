import sys
import csv
import datetime



class Option:
	symbol = ""
	strike = 0
	expiration = datetime.date(2000,1,1)
	contract_type = ""
	price = 0.0

	def __init__(self,symbol,strike,expiration,contract_type, price):
		self.symbol = symbol
		self.strike = strike
		self.expiration = expiration
		self.contract_type = contract_type
		self.price = price


	def isExpired(self):
		if self.expiration < datetime.date.today():
			return(True)
		else:
			return(False) 

	def equals(self,option):
		b1 = option.symbol == self.symbol
		b2 = option.strike == self.strike
		b3 = option.expiration == self.expiration
		b4 = option.contract_type == self.contract_type
		if b1 & b2 & b3 & b4 :
			return(True)
		else:
			return(False)







class Stock:
	symbol = ""
	price = 0.0

	def __init__(self,symbol,price):
		self.symbol = symbol
		self.price = price


	def equals(self,option):
		if option.symbol == self.symbol:
			return(True)
		else:
			return(False)






class StockTrade:

	# Fields:
	contract = None

	symbol = ""
	n = 0
	tradedate   = datetime.date(2000,1,1)
	tradeclosed = None
	pnl = 0
	fee = 0.0
	openTrade = False


	# Constructor:
	def __init__(self,trade_contract,N,tradedate):
		self.contract = trade_contract
		self.n = N
		self.tradedate = tradedate
		self.openTrade = True
		self.symbol = trade_contract.symbol

	def sameContract(self,stock):
		if type(stock).__name__ != "StockTrade":
			return(False)

		if self.contract.equals(stock.contract):
			return(True)
		else:
			return(False)	

	def printMe(self):
		print(self.contract.symbol)
		print("Type: Stock")
		print("Open: " + str(self.openTrade))
		print("N: " + str(self.n))
		print("Filled: \t" + self.tradedate.strftime("%b %d, %Y"))
		if not self.openTrade:
			print("Closed: \t" + self.tradeclosed.strftime("%b %d, %Y"))
		print("Price: " + str(self.contract.price))
		print("PnL: " + str(self.pnl))	

	def addTrade(self,stock):
		delta = self.contract.price - stock.contract.price	
		self.pnl += delta * stock.n
		self.n += stock.n

		if self.n == 0:
			self.openTrade = False
			self.tradeclosed = stock.tradedate







class OptionsTrade:

	# Fields:
	contract = None
	
	symbol = ""
	n = 0
	tradedate   = datetime.date(2000,1,1)
	tradeclosed = None
	expiration  = datetime.date(2000,1,1)
	price = 0.0
	pnl = 0
	openTrade = False
	fee = 0.0
	

	# Constructor:
	def __init__(self,trade_contract,N,tradedate):
		self.contract = trade_contract
		self.n = N
		self.tradedate = tradedate
		self.symbol = trade_contract.symbol
		self.expiration = trade_contract.expiration
		self.openTrade = True

	def printMe(self):
		print(self.symbol)
		print("Type: Single")
		print("Open: " + str(self.openTrade))
		print("N: " + str(self.n))
		print(self.contract.contract_type)
		print("Filled: \t" + self.tradedate.strftime("%b %d, %Y"))
		if not self.openTrade:
			print("Closed: \t" + self.tradeclosed.strftime("%b %d, %Y"))
		print("Expires:\t" + self.expiration.strftime("%b %d, %Y"))
		print("Strike: " + str(self.contract.strike))
		print("PnL: " + str(self.pnl))

	def isExpired(self):
		return(self.contract.isExpired())
	def expired(self):
		if self.openTrade:
			self.pnl -= self.contract.price * self.n * 100
			self.openTrade = False
			self.tradeclosed = self.expiration

	def addTrade(self,option):
		delta = self.contract.price - option.contract.price	
		self.pnl += delta * option.n * 100
		self.n += option.n
		if self.n == 0:
			self.openTrade = False
			self.tradeclosed = option.tradedate


	def sameContract(self,option):
		if type(option).__name__ != "OptionsTrade":
			return(False)

		if self.contract.equals(option.contract):
			return(True)
		else:
			return(False)		


class IronCondor:
	long_put   = None
	short_put  = None
	short_call = None
	long_call  = None
	
	symbol = ""
	n = 0
	tradedate   = datetime.date(2000,1,1)
	tradeclosed = None
	expiration  = datetime.date(2000,1,1)
	price = 0.0
	pnl = 0
	openTrade = False
	
	
	

	# Constructor:
	def __init__(self,contracts):
		self.symbol = contracts[0].contract.symbol
		self.tradedate = contracts[0].tradedate
		self.expiration = contracts[0].contract.expiration
		self.openTrade = True

		strikes = [0]*4
		for i in range(4):
			strikes[i] = contracts[i].contract.strike
			self.price += contracts[i].contract.price * (abs(contracts[i].n)/contracts[i].n)

		self.n = int(abs(contracts[0].n) * abs(self.price)/self.price)
		self.price = abs(self.price)
		self.long_put = contracts[strikes.index(sorted(strikes)[0])]
		self.short_put = contracts[strikes.index(sorted(strikes)[1])]
		self.short_call = contracts[strikes.index(sorted(strikes)[2])]
		self.long_call = contracts[strikes.index(sorted(strikes)[3])]


	def printMe(self):
		print(self.symbol)
		print("Type: Iron Condor")
		print("Open: " + str(self.openTrade))
		print("N: " + str(self.n))
		print("Max Loss: " + str(self.maxLoss()))
		print("Price: " + str(self.price))
		print("Cost: " + str(self.price*self.n*100))
		print("Filled: \t" + self.tradedate.strftime("%b %d, %Y"))
		if not self.openTrade:
			print("Closed: \t" + self.tradeclosed.strftime("%b %d, %Y"))
		print("Expires:\t" + self.expiration.strftime("%b %d, %Y"))
		print(self.long_put.contract.strike)
		print(self.short_put.contract.strike)
		print(self.short_call.contract.strike)
		print(self.long_call.contract.strike)
		print("PnL: " + str(self.pnl))


	def maxLoss(self):	
		spread = max(self.short_put.contract.strike - self.long_put.contract.strike,self.long_call.contract.strike - self.short_call.contract.strike)
		return((spread - self.price)*100*self.n)

	def isExpired(self):
		return(self.long_put.contract.isExpired())
	def expired(self):
		if self.openTrade:
			self.long_put.expired()
			self.short_put.expired()
			self.short_call.expired()
			self.long_call.expired()
			self.pnl = self.long_put.pnl + self.short_put.pnl + self.short_call.pnl + self.long_call.pnl
			self.openTrade = False
			self.tradeclosed = self.expiration

	def sameContract(self,ic):
		if type(ic).__name__ != "IronCondor":
			return(False)

		b1 = self.long_put.sameContract(ic.long_put)
		b2 = self.short_put.sameContract(ic.short_put)
		b3 = self.short_call.sameContract(ic.short_call)
		b4 = self.long_call.sameContract(ic.long_call)

		if b1 & b2 & b3 & b4:
			return(True)
		else:
			return(False)


	def addTrade(self,ic):
		self.long_put.addTrade(ic.long_put)
		self.short_put.addTrade(ic.short_put) 
		self.short_call.addTrade(ic.short_call)
		self.long_call.addTrade(ic.long_call) 
		self.pnl = self.long_put.pnl + self.short_put.pnl + self.short_call.pnl + self.long_call.pnl	

		self.n += ic.n
		if self.n == 0:
			self.openTrade = False
			self.tradeclosed = ic.tradedate




class CalandarSpread:

	front_leg = None
	back_leg = None

	symbol = ""
	n = 0
	tradedate   = datetime.date(2000,1,1)
	tradeclosed = None
	expiration  = (datetime.date(2000,1,1),datetime.date(2000,1,1))
	price = 0.0
	pnl = 0
	openTrade = False



	# Constructor:
	def __init__(self,contracts):
		self.symbol = contracts[0].contract.symbol
		self.tradedate = contracts[0].tradedate
		self.openTrade = True

		# sort by expiration date
		expiries = [0]*2
		for i in range(2):
			expiries[i] = contracts[i].contract.expiration
			self.price += contracts[i].contract.price * (abs(contracts[i].n)/contracts[i].n)
		# n < 0 iff price < 0
		self.n = int(abs(contracts[0].n) * abs(self.price)/self.price)
		self.price = abs(self.price)
		
		self.front_leg = contracts[expiries.index(sorted(expiries)[0])]
		self.back_leg = contracts[expiries.index(sorted(expiries)[1])]
		self.expiration = (sorted(expiries)[0],sorted(expiries)[1])


	def printMe(self):
		print(self.symbol)
		print("Type: Calandar Spread")
		print("Open: " + str(self.openTrade))
		print("N: " + str(self.n))
		# print("Max Loss: " + str(self.maxLoss()))
		print("Price: " + str(self.price))
		print("Cost: " + str(self.price*self.n*100))
		print("Filled: \t" + self.tradedate.strftime("%b %d, %Y"))
		if not self.openTrade:
			print("Closed: \t" + self.tradeclosed.strftime("%b %d, %Y"))
		print("Expires:\t" + self.front_leg.expiration.strftime("%b %d, %Y"))
		print("Strike: " + str(self.front_leg.contract.strike))
		print("PnL: " + str(self.pnl))

	def isExpired(self):
		return(self.front_leg.contract.isExpired())
	def expired(self):
		if self.openTrade:
			self.front_leg.expired()
			self.back_leg.expired()
			self.pnl = self.front_leg.pnl + self.back_leg.pnl
			self.openTrade = False
			self.tradeclosed = self.expiration

	def addTrade(self,calspread):
		self.front_leg.addTrade(calspread.front_leg)
		self.back_leg.addTrade(calspread.back_leg) 
		self.pnl = self.front_leg.pnl + self.back_leg.pnl

		self.n += calspread.n
		if self.n == 0:
			self.openTrade = False
			self.tradeclosed = calspread.tradedate

	def sameContract(self,calspread):
		if type(calspread).__name__ != "CalandarSpread":
			return(False)
		b1 = self.front_leg.sameContract(calspread.front_leg)
		b2 = self.back_leg.sameContract(calspread.back_leg)
		if b1 & b2:
			return(True)
		else:
			return(False)








class VerticalSpread:

	lower_leg = None	# lower strike
	upper_leg = None	# higher strike

	symbol = ""
	n = 0
	tradedate   = datetime.date(2000,1,1)
	tradeclosed = None
	expiration  = datetime.date(2000,1,1)
	price = 0.0
	pnl = 0
	openTrade = False


	

	# Constructor:
	def __init__(self,contracts):
		self.symbol = contracts[0].contract.symbol
		self.tradedate = contracts[0].tradedate
		self.expiration = contracts[0].expiration
		self.openTrade = True

		# sort by strikes
		strikes = [0]*2
		for i in range(2):
			strikes[i] = contracts[i].contract.strike
			self.price += contracts[i].contract.price * (abs(contracts[i].n)/contracts[i].n)
		# n < 0 iff price < 0
		self.n = int(abs(contracts[0].n) * abs(self.price)/self.price)
		self.price = abs(self.price)

		self.lower_leg = contracts[strikes.index(sorted(strikes)[0])]
		self.upper_leg = contracts[strikes.index(sorted(strikes)[1])]


	def printMe(self):
		print(self.symbol)
		print("Type: Vertical Spread")
		print("Open: " + str(self.openTrade))
		print("N: " + str(self.n))
		# print("Max Loss: " + str(self.maxLoss()))
		print("Price: " + str(self.price))
		print("Cost: " + str(self.price*self.n*100))
		print("Filled: \t" + self.tradedate.strftime("%b %d, %Y"))
		if not self.openTrade:
			print("Closed: \t" + self.tradeclosed.strftime("%b %d, %Y"))
		print("Expires:\t" + self.expiration.strftime("%b %d, %Y"))
		print(self.lower_leg.contract.strike)
		print(self.upper_leg.contract.strike)
		print("PnL: " + str(self.pnl))

	def isExpired(self):
		return(self.lower_leg.contract.isExpired())
	def expired(self):
		if self.openTrade:		
			self.lower_leg.expired()
			self.upper_leg.expired()
			self.pnl = self.lower_leg.pnl + self.upper_leg.pnl
			self.openTrade = False
			self.tradeclosed = self.expiration

	def sameContract(self,vertspread):
		if type(vertspread).__name__ != "VerticalSpread":
			return(False)
		b1 = self.lower_leg.sameContract(vertspread.lower_leg)
		b2 = self.upper_leg.sameContract(vertspread.upper_leg)
		if b1 & b2:
			return(True)
		else:
			return(False)


	def addTrade(self,vertspread):
		self.lower_leg.addTrade(vertspread.lower_leg)
		self.upper_leg.addTrade(vertspread.upper_leg) 
		self.pnl = self.lower_leg.pnl + self.upper_leg.pnl

		self.n += vertspread.n
		if self.n == 0:
			self.openTrade = False
			self.tradeclosed = vertspread.tradedate









class ClosedTrade:


	symbol = None
	spread = None
	tradedate   = None
	expiration  = False
	tradeclosed = None
	method = None
	pnl = 0
	

	def __init__(self,trade):
		if not trade.openTrade:
			self.symbol = trade.symbol
			self.spread = type(trade).__name__
			self.tradedate = trade.tradedate
			self.tradeclosed = trade.tradeclosed
			self.pnl = trade.pnl

			if hasattr(trade, 'expiration'):
				if type(trade.expiration) == tuple :
					self.expiration = trade.expiration[0]
				else:
					self.expiration = trade.expiration
				if self.tradeclosed == self.expiration:
					self.method = "Expired"
				else: 
					self.method = "Managed"
			else:
				self.method = "Managed"

	def printMe(self):
		print(self.symbol)
		print(self.spread)
		print("Opened: " + self.tradedate.strftime("%b %d, %Y"))
		if self.expiration:
			print("Expiration: " + self.expiration.strftime("%b %d, %Y"))
		else:
			print("Expiration: ")
		print("Closed: " + self.tradeclosed.strftime("%b %d, %Y"))
		print("Method: " + self.method)
		print("PnL: " + str(round(self.pnl)))


	def toList(self):
		l = []
		l.append(self.symbol)
		l.append(self.spread)
		l.append(self.tradedate.strftime("%b %d, %Y"))
		if self.expiration:
			l.append(self.expiration.strftime("%b %d, %Y"))
		else: 
			l.append("NA")
		l.append(self.tradeclosed.strftime("%b %d, %Y"))
		l.append(self.method)
		l.append(round(self.pnl,2))

		return(l)

	def attrList(self):
		return(["Symbol","Type","Opened","Expiration","Closed","Management","PnL"])












