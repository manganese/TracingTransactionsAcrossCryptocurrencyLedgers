'''
PassThrough and Augmented Phase 1 of 'Tracing transactions across cryptocurrency ledgers.

This script requires earlier backend running of haaroonys code which means there must be blocksci
running for BTC, DASH, ZEC, LTC and parquet files.
 
This script also requires running og MakingPickles.py first for each of BCH, ETC, ETH and DOGE.

The requirements regard the blockchain data which we will query for our front end analysis.


1. Make transactions.csv using Haaroony's code, which represents the scrapped transactions from ShapeShift. 
The csv should look like that:

Value,Pair,SS_Timestamp,Index

0.40558177,ETH_BTC,1515264203,1300000
0.601,LTC_LBC,1515249165,1300001
0.48925603,ETH_LTC,1515199302,1300002
9541.17186613,DOGE_ETH,1515266406,1300003
0.07233796,LTC_DOGE,1515216440,1300004
0.02012882,ETH_RDD,1515233600,1300005
1900.0,XRP_BTC,1515207093,1300006
1.05032948,ETH_BTC,1515207994,1300007
182.66108542,RLC_LTC,1515272613,1300008

2. mkdir BlocksciChains and put there the blocksci chains. Name them zcash, litecoin, bitcoin, dash

3. mkdir PickledFiles and Run MakingPickles.py for BCH, ETC, ETH and DOGE. 
Each coin will create 2 pickle files, CoinVouts.pkl and CoinBlocks.pkl. Put all 8 pickle files in PickledFiles. 

4. mkdir Phase1Results, AugmentedResults, in these directories the Phase1 and Augmented results will be stores, accordingly. 
In order to run Augmented for Coin, you need to run Phase1 for Coin. 

'''

import csv
from collections import Counter
import operator
import blocksci
import shapeshiftFunctions
import pickle 
import sys
import requests
import pandas as pandas
import os

def loadTransactions():

	transactions = []

	with open('Transactions.csv','r') as fr:
		
		reader=csv.reader(fr)
		
		for row in reader:
			transactions.append(row)

	transactions=transactions[1:]

	transactions={int(t[-1]): ( float(t[0]) , t[1] , int(t[2]) , int(t[3]) ) for t in transactions}

	return transactions

def runPhase1(blocks_before,blocks_ahead,coin):

	ss_data="Transactions.csv"

	if coin == "ZEC":
		filename = "zcash"
	elif coin == "LTC":
		filename = "litecoin"
	if coin == "DASH":
		filename = "dash"
	if coin == "BTC":
		filename = "bitcoin"

	chain = blocksci.Blockchain('BlocksciChains/'+filename)
	sstx = shapeshiftFunctions.loadShapeShiftRates(path=ss_data, curIn=coin)
	txs = shapeshiftFunctions.findSimilarTxPhase1(chain=chain, sstxes=sstx, blocks_ahead=blocks_ahead, blocks_before=blocks_before) 

	return txs

def runAugmentedPhase1(coin,txs,transactions):

	phase1Aug={}                                    
	
	if coin == "ZEC":
		filename = "zcash"
	elif coin == "LTC":
		filename = "litecoin"
	if coin == "DASH":
		filename = "dash"
	if coin == "BTC":
		filename = "bitcoin"

	chain = blocksci.Blockchain('BlocksciChains/'+filename)

	for shapeshiftTx,possibleTxs in txs.items():
		
		phase1Aug[shapeshiftTx]=set()
		
		for blocksciIndex in possibleTxs:
			for output in chain.tx_with_index(blocksciIndex).outputs:
				if output.value == int(transactions[shapeshiftTx][0]*pow(10,8)):
					phase1Aug[shapeshiftTx].add(output.address.address_string)

	addresses = set()

	for v in phase1Aug.values():
		addresses=addresses.union(v)

	addressToAPi={}
	ctr=0
	failed=set()

	for address in addresses:
	
		if ctr%10==0:
			print("Querried {} out of {}. {} failed.".format(ctr,len(addresses),len(failed)))
		try:
			addressToAPi[address] = requests.get("https://cors.shapeshift.io/txStat/"+address).json() #Make the request using the address
		except:
			failed.add(address)

		ctr+=1

	return phase1Aug,addressToAPi

def runAugmentedPhase2(coin,txs,transactions):


	phase1Aug=txs                                    
	
	addresses = set()

	for v in phase1Aug.values():
		addresses=addresses.union(v)

	addressToAPi={}
	ctr=0
	failed=set()

	print(len(addresses))
	for address in addresses:
	
		if ctr%10==0:
			print("Querried {} out of {}. {} failed.".format(ctr,len(addresses),len(failed)))
		try:
			addressToAPi[address] = requests.get("https://cors.shapeshift.io/txStat/"+address).json() #Make the request using the address
		except:
			failed.add(address)

		ctr+=1

	return phase1Aug,addressToAPi

def cleanAndDump(txs,coin):
	results={}
	for row in txs:
		results[row['shapeshift_tx']._4]=[]
		for candidate in row['possible_txs']:
			results[row['shapeshift_tx']._4].append(candidate.index)

	pickle.dump(results,open('Phase1Results/Phase1{}.pkl'.format(coin),'wb'))

	return results


if __name__ == "__main__":
	
	#This is where Phase1 Begins
	
	print("Initiating Phase1...")
	accept = ["LTC","ZEC","DOGE","DASH","ETH","ETC","BCH","BTC"]
	
	transactions = loadTransactions()

	while True:
		
		coin = input("Type your preference (BTC/BCH/ETC/ETH/ZEC/LTC/DASH/DOGE) or EXIT: ")
		
		#Checking whether the coin oprtion was valid.
		if coin not in accept and coin!="EXIT":
			print("Enter a valid option!")
			continue
		
		elif coin == "EXIT":
			break

		#According to our paper, the best possible params are: 
		
		# BTC --->  Before: 0 , After: 1 
		# BCH --->  Before: 9 , After: 4
		# DASH -->  Before: 5 , After: 5
		# DOGE -->  Before: 1 , After: 4
		# ETH --->  Before: 5 , After: 0
		# ETC --->  Before: 5 , After: 0
		# LTC --->  Before: 1 , After: 2
		# ZEC --->  Before: 1 , After: 3

		#Checking whether the blocks_before option is valid.
		while  True:
			
			blocks_before=int(input("Enter blocks before (0-30): "))
			
			if float(blocks_before)<0 or float(blocks_before)>30:
				print("Enter a valid option!")
				continue
			else:
				break  

		#Checking whether the blocks_ahead option is valid.
		while  True:
			
			blocks_ahead=int(input("Enter blocks ahead (0-30): "))
			
			if float(blocks_ahead)<0 or float(blocks_ahead)>30:
				print("Enter a valid option!")
				continue
			else:
				break  


		if coin in ["BTC","ZEC","LTC","DASH"]:

			txs = runPhase1(int(blocks_before), int(blocks_ahead), coin)
			print("Done!")
			
			print('Cleaning and dumping...')
			cleanAndDump(txs,coin)
			print('Done')
			print()
		
		else:
			
			print("Loading Vouts and Blocks, may take time...")
			vouts = pickle.load(open("PickledFiles/{}Vouts.pkl".format(coin),"rb"))
			blocks = pickle.load(open("PickledFiles/{}Blocks.pkl".format(coin),"rb"))
			print('Done!')
			print()
			s = set(blocks.keys())

			phase1 = [list(t) for t in transactions.values() if t[1].split("_")[0] == coin]
			
			#Find the closest block to each Shapeshift transaction.
			for tx in phase1:
				
				shapeshiftTimestamp = tx[2]

				while True:

					if shapeshiftTimestamp in s:

						tx.append(blocks[shapeshiftTimestamp])
						break 

					else:

						shapeshiftTimestamp+=1

			txs={}

			phase1Length = len(phase1)
			print("{} has {} transaction as curIn.".format(coin,phase1Length))
			print()
			ctr=0

			for tx in phase1:

				shapeshiftValue = tx[0] 
				shapeshiftPair = tx[1]
				shapeshiftTimestamp = tx[2]
				shapeshiftIndex = tx[3]
				closestBlock = tx[4]
				
				results = set()

				for blockIndex in range(closestBlock - blocks_before , closestBlock + blocks_ahead):

					for vout in vouts[blockIndex]:

						blockchainAddress = vout[0]
						blockchainValue = vout[1]

						#If you are dealing with ETH, ETC you may need to tweak the code here to add an error rate of 1% because of the decimal accuracy
						if blockchainValue > 0.99*shapeshiftValue and blockchainValue < 1.01*shapeshiftValue :
							results.add(blockchainAddress)

				txs[shapeshiftIndex]=results
				
				if ctr%10==0:
					print("Progress: {} out of {}.".format(ctr,phase1Length))
				
				ctr+=1
			print("Done!")
			print()
			print('Cleaning and dumping...')
			pickle.dump(txs,open('Phase1Results/Phase1{}.pkl'.format(coin),'wb'))
			print("Done!")

	#This is where AugmentedPhase Begins
	
	print("Initiating Augmenting Phase...")
	accept = ["LTC","ZEC","DOGE","DASH","ETH","ETC","BCH","BTC"]
	
	while True:
		
		coin = input("Type your preference (BTC/BCH/ETC/ETH/ZEC/LTC/DASH/DOGE) or EXIT: ")
		
		#Checking whether the coin oprtion was valid.
		if coin not in accept and coin!="EXIT":
			print("Enter a valid option!")
			continue
		
		elif coin == "EXIT":
			break

		try:
			phase1Txs = pickle.load(open('Phase1Results/Phase1{}.pkl'.format(coin),'rb'))
		except:
			print('Phase 1 Results not found for this coin! You need to run Phase1 before you run Augmented.')
			continue

		print('Running Augmented for {}. Highly recommended to partition the querries over multiple machines as the API rate limits per IP address.'.format(coin))

		if coin in ["LTC","ZEC","DASH","BTC"]:
			
			phase1Aug,addressToAPi=runAugmentedPhase1(coin,phase1Txs,transactions)
			
		elif coin in ["ETC","ETH","BCH","DOGE"]:

			phase1Aug,addressToAPi=runAugmentedPhase2(coin,phase1Txs,transactions)

		augFinal={}
			
		for k,v in phase1Aug.items():
				
			tmp=[]
				
			for addr in v:
				
				if addressToAPi[addr]['status']=='resolved' or addressToAPi[addr]['status']=='complete':
				
					tmp.append(addressToAPi[addr])
				
			augFinal[k]=tmp

		pickle.dump(augFinal,open('AugmentedResults/{}Augmented.pkl'.format(coin),'wb'))

