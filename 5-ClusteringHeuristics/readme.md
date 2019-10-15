# Clustering Heuristics - Common Relationship Heuristic

    If two or more addresses send coins to the same address in the curOut blockchain, 
    or if two or more addresses receive coins from the same address in the curIn 
    blockchain, then these addresses have some common social relationship.
    
This program takes in multiple `.pkl` files which contain the information linking both phase1 and phase2 transctions. 

`.pkl` is a dictionary which contains a key to the transaction id, value with transaction details. 

    e.g. 
    In [5]: x[3145650]
    Out[5]:
    [{'status': 'complete',
      'outgoingCoin': '0.01497222',
      'transaction': '8e5016b730a34817fb91ac36afcc45b17d0cb60f5c4a7a69c3c1a7ea50dd7875',
      'outgoingType': 'BTC',
      'incomingType': 'BCH',
      'address': '1DXpszo6rM5xzjNcdp14h6aPE2CP35toNg',
      'withdraw': '1Pz4Wr28ThUib759UFcuXdwrKrpMCZ3HWZ',
      'incomingCoin': 0.11047788,
      'Phase1': {'Hash': '3bb501ae97a1a4bbf74a9b220bc67bebce381a5e0404d738af1fb9f542b7d8c0',
       'Addresses': {'14Rk6vyms4orz8hyTr2dLEAEm43LSDBeGx',
        '1LRpFKUMUiFDfiz3FSKF4QvPQpUxLn14HG'},
       'Spents': {'2417948cc53bdbae2ff7db57bbdf354f93320745218a776e5282263101396c23',
        'bc75946f46d23840dfc132e755c94c88b327c8af43f66c640e10c3c6bc7e8e9d'}},
      'transactionURL': 'https://blockchain.info/tx/8e5016b730a34817fb91ac36afcc45b17d0cb60f5c4a7a69c3c1a7ea50dd7875'}]

The information from here is extracted, namely the input address `Phase1 > Addresses` and output address `address` and draws an edge between them as they had been involved in a shift. This is processed as a networkx directed graph and then the results are shown on screen. 

Its advised to run this in an interactive python shell so the graph can be dumped, drawn and further explored. 