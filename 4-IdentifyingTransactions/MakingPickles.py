'''
Making the big ugly pickle files for ETH, ETC, DOGE and BCH cause Blocksci doesn't want to work for them.
Making these files will make the Phase1 and Augmented Phase much easier and faster. 
Very long computations, memory intensive, use servers. 


1. Setup the PySpark environment as speicified in Haaroon's section. 

2. mkdir BCH, ETC, ETH, DOGE

3. mkdir coin/vouts and coin coin/blocks for each of the 4 coins and add there the vout and block parquets, accordingly. For account 
based coins (ETC, ETH) the vout parquets are basically the transaction parquets. 

4. Every time you want to get vouts and blocks for a coin, cd coin, run pyspark and run the script

5. Run the code for BCH, ETC, ETH, DOGE and once the vouts.pkl and blocks.pkl are created you may proceed to TransactionAnalysis.py to start getting some results. 

6. Before running the code, pick coin, minBlock and maxBlock, as the script runs in pyspark environment and cant pass arguments 

WARNINGS: 
1. CoinVouts.pkl and CoinBlocks.pkl take time to be created and take a lot of space in memory to be created and in disk to be stores.
Using personal computers to create them is advised against.

2. The columns of the parquet files are assumed to be:
-- tx_to for each output address
-- tx_value for each output value
-- block_timestamp for each block timestamp
-- block_number for each block height
Upon creating the Parquet files, maintain consistency. If they are already created, tweak the code below for each coin, according to the column names you gave.
'''

from pyspark import SparkContext
from pyspark.sql import SQLContext
import pickle

sql_sc = SQLContext(sc)

coin = 'ETC' # Pick your coin here (BTC, BCH, ETC, ETH, ZEC, DASH, DOGE, LTC) 
minBlock = 5150000 # Pick the minimum block number of your search scope (Put the closest block of your first scrapped ShapeShift transaction with this coin as curIn)
maxBlock = 5200000 # Same with maximum

vouts={block:[] for block in range(minBlock,maxBlock+1)}
 
filenames = [filename for filename in os.listdir("transactions/") if 'parquet' in filename]
 
ctr=0
totalParquets = len(filenames)
 
for filename in filenames:

	print('Working with filename: {}'.format(filename))

	df = sql_sc.read.parquet('transactions/{}'.format(filename)).collect()
	
	for row in df:
		if row.tx_block_number >= minBlock and row.tx_block_number <= maxBlock:
			vouts[row.tx_block_number].append( ( row.tx_to , float(row.tx_value) * pow(10,-18) ) )

		if ctr%10==0:
			print("Progress: {} out of {}.".format(ctr,totalParquets))

		Ictr+=1    

blocks={}
filenames = [filename for filename in os.listdir("blocks/") if 'parquet' in filename] 

ctr=0
totalParquets = len(filenames)

for filename in filenames:

	print('Working with filename: {}'.format(filename))

	df = sql_sc.read.parquet('blocks/{}'.format(filename)).collect()

	for row in df:
		blocks[row.block_timestamp]=row.block_number

	if ctr%10==0:
		print("Progress: {} out of {}.".format(ctr,totalParquets))

	ctr+=1   
 
print('Dumping the results...')
pickle.dump(vouts,open('{}Vouts.pkl'.format(coin),'wb'))
pickle.dump(vouts,open('{}Blocks.pkl'.format(coin),'wb'))
