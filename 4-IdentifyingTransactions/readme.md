 
# Identifying Transactions

There are two parts to finding the full transaction which we call Phase 1 and Phase 2. 

Phase 1 - Find the input transaction on the blockchain using TransactionAnalysis.py

Phase 2 - Finds the corresponding output transaction by using the ShapeShift API using the second part of TransactionAnalysis.py

## Prepering to identify the transactions 

Blocksci - Run BTC, DASH, ZEC and LTC Blocksci chains and follow the steps specified in TransactionAnalysis.py

Parquets - ETC, ETH, DOGE and BCH can't be supported by Blocksci so Haaroony made Parquet files. Make them following his instructions and make sure the column names of the dataframes have the names specified in the instructions in TransactionAnalysis.py. The directory where they are held is also specified in TransactionAnalysis.py

## Phase 1
### Blocksci parsed chains

We parsed BTC, LTC, DASH and ZEC with Blocksci. For this task we use a combination of TransactionAnalysis.py and 
shapeshiftFunctions.py to produce the results. Phase1 Results are represented as Python dictionaries and are in the following format for Blocksci parsed chains: 

 1309917: [2077216, 2077297],
 
 1309952: [2076881],
 
 1309977: [2071786],
 
 1309989: [2068396],
 
 1309991: [2069994]

Every key represents the unique ShapeShift transaction identifier as shown in Trasactions.csv. Every Value is a list of candidates that represents the blockchain transactions that we think corresponds to the ShapeShift transaction. This list can be empty, if we find no candidates, single hit or multihit. The Blockchain transactions are themselves represented as a uniquely identifiable index that corresponds to the transaction Blocksci index. 

### Parquet chains

We parsed ETH, ETC, DOGE and BCH data with Spark into Parquet files. Use the instructions in MakingPickles.py in order to read those Parquet files and produce for each coin 2 necessary and big Pickle files named CoinVouts.pkl and BlocksVouts.pkl. You cannot run Phase1 or AugmentedPhase without those files. Phase1 Results are represented as Python dictionaries and are in the following format for Blocksci parsed chains: 
 
 1305348: {'0x8837234b8d27cf4abdae353264f45c8866631ed5'},
 
 1305428: set(),
 
 1305480: {'0x8837234b8d27cf4abdae353264f45c8866631ed5'},
 
 1305488: {'0x0ed348d134c93e642173c0bed3be00534b8cb664'},
 
 1305884: set(),
 
 1306086: {'0x8837234b8d27cf4abdae353264f45c8866631ed5'},
 
 1306165: set(),
 
 1306199: {'0x82f9fbd57d31d048a2e95d418bb818e8c15e2307'
 
Every key represents the unique ShapeShift transaction identifier as shown in Trasactions.csv. Every Value is a set of candidates that represents the output addresses that we think belong to ShapeShift and are the recipients of deposits. These sets can be empty, if we find no candidates, single hit or multihit. 

## Phase 2  

For Phase2 or AugmentedPhase, we use the Shapeshift API provided. It is included in TransactionAnalysis.py. You cannot run Augmented for a coin if Phase1 is not run FIRST. The results of Augmented for each coin is in the following format: 

1309483: [{'address': 't1bim7W9RRivo42e62AsnNiuu7UQCNyCf2u',
   
   'incomingCoin': 0.05,
   
   'incomingType': 'ZEC',
   
   'outgoingCoin': '17.10246233',
   
   'outgoingType': 'GNT',
   
   'status': 'complete',
   
   'transaction': '0xa547b269803af50cbf384547f9d1b55454d6000877c70467fdd7577840736e6c',
   
   'transactionURL': 'https://etherscan.io/tx/0xa547b269803af50cbf384547f9d1b55454d6000877c70467fdd7577840736e6c',
   
   'withdraw': '0x8f1bec38a52c187f3b10fea9b46fafdad0c98e09'}],
   
   
 
 1309489: [],
 
 
 
 1309530: [{'address': 't1eSRe4jrW7T3LJ9Y62sAFrNzGRGCTahLoY',
 
   'incomingCoin': 0.09774,
 
   'incomingType': 'ZEC',
   
   'outgoingCoin': '3882.6337288',
   
   'outgoingType': 'DOGE',
   
   'status': 'complete',
   
   'transaction': 'af58546889789af87f32490d9b1e934229ca611feecd491de48d6884ad0b7f9e',
   
   'transactionURL': 'https://dogechain.info/tx/af58546889789af87f32490d9b1e934229ca611feecd491de48d6884ad0b7f9e',
   
   'withdraw': 'DGrrUXp5JnbnT2PjaQuifHJYwiUZ9ciBmj'}]


Every key represents the unique ShapeShift transaction identifier as shown in Trasactions.csv. Every Value is a list of candidates that represents the full flow of money, from the deposit in the curIn chain to the withdrawal in the curOut chain. These lists can be empty, if we find no candidates, single hit or multihit.
