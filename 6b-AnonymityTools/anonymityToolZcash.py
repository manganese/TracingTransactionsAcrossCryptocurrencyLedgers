__author__ = 'haaroony'
'''
This script contains methods that look at interactions between ShapeShift and the shielded pool. 
            
                        Interaction A
    --------------      -----------     -----------------
    | ShapeShift | ---> | address | --> | shielded pool |
    --------------      -----------     -----------------
           ^                                     |
           |                                     |
           |-------------------------------------|
                        Interaction B

Interaction A is whether a user does a ShapeShift and then sends the money into the pool 
(ShapeShift -> address -> pool).
Interaction B is when a user sends money from the pool directly to ShapeShift 
(pool -> ShapeShift).
'''

import blocksci

'''

Parameters:
    chain: blocksci zcash chain object
    zcashp1tx: zcash phase 1 transactions in the format
                    {
                    'shapeshift tx index': [blockchain tx id..],
                    ...
                }
    zcashp2tx: zcash phase 2 transactions in the format
                {
                    'shapeshift tx index': [blockchain tx id..],
                    ...
                }
    sscluster: a list of addresses in the shapeshift cluster           
    transactions: a list of shapeshift in the format below,
    where the 'shapeshift tx index' above corresponds to the 
    transaction at the same index
        e.g.[
             [1515199132,           #timestamp
              0.01,                 #feee
              200.53933771,         #amount
              '06012018',           #date
              8.13071075,           #rate
              'LBC_DGB',            #pair
              1515199153,           #rate time
              229.26076457845082],  #usd value
              [...
        ...
        ]
'''

def interactionAandB(chain, zcashp1tx, zcashp2tx, zcashtransactions):
    straightIntoPool = []
    # Get the one hit wonders
    straightindexes = []
    for x in zcashp2tx:
        if len(zcashp2tx[x])==1:
            straightindexes.extend(zcashp2tx[x])
    txs = chain.filter_txes(lambda t: t.block_height > 180742 and t.index in straightindexes)

    # for each tx with one hit:
    found=0
    tempcount = 0
    totalval = 0
    totalpoolval = 0
    straightIntoPool=[]
    skipped=0
    for ssindex in zcashp2tx:
        tempcount+=1
        if tempcount % 100 == 0:
            print(str(tempcount)+"/"+str(len(zcashp2tx)))
        if len(zcashp2tx[ssindex])==0:
            continue
        for tx in zcashp2tx[ssindex]:
            if tx['status'] != 'complete':
                continue
            try:
                blktx = chain.tx_with_hash(tx['transaction'])
            except RuntimeError:
                skipped+=1
                continue
            # compute exchange vzcalue of ss tx
            if 'outgoingCoin' not in tx:
                continue
            zecValue = int(float(tx['outgoingCoin'])*1e8)
            totalval += zecValue
            # find the output
            for out in blktx.outs:
                if out.value == zecValue and out.is_spent:
                    found+=1
                # see if it was spent
                    # if spent, check if it went to a node out of the cluster
                    spentTxIndex = out.spending_tx_index
                    spentTx = chain.tx_with_index(spentTxIndex)
                    # if unspent then ignore
                    if spentTx == 0:
                        continue

                    if spentTx.output_count == 0:
                        totalpoolval += out.value
                        straightIntoPool.append(spentTx)

    print('all p2 txs ' + str(len(zcashp2tx)))
    print("Interaction A: Total txs into pool:" + str(len(straightIntoPool)))
    print("Interaction A: Total coins into pool:   " + str(totalpoolval))
    print('total value of zcash p2 ' + str(totalzecp2))


    # Interaction B
    tempcount = 0
    frompool = 0
    totalfrompool = 0
    for ssindex in zcashp1tx:
        tempcount+=1
        if tempcount % 5000 == 0:
            print(str(tempcount)+"/"+str(len(zcashp1tx)))
        if len(zcashp1tx[ssindex])!=1:
            continue
        txindex = zcashp1tx[ssindex][0]
        tx = None
        for a in txs:
            if a.index == txindex:
                tx = a
                break
        if tx is None:
            print('didnt find')
            continue
        sstx = zcashtransactions[ssindex]
        # compute exchange value of ss tx
        zecValue = sstx[2]*1e8
        # find the output
        d = False
        for out in tx.outs:
            if d:
                continue
            # see if it was spent
            if zecValue == out.value and len(tx.ins) == 0:
                frompool += 1
                totalfrompool += zecValue
                d = True


    print("Interaction B: Total txs from pool   : " + str(len(frompool)))
    print('Interaction B: Total coins from pool : ' + str(totalfrompool/1e8))
