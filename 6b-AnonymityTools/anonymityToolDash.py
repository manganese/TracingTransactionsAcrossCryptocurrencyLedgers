__author__ = 'haaroony'
'''

This script looks at identifying the following: 
Interaction A: Did users who received money from ShapeShift perform a coinjoin right after?
Interaction B: Were coins sent to ShapeShift obtained from a coinjoin?

Our rules for whether a transaction is a coinjoin are:
    - more than 2 inputs
    - more than 2 outputs
    - all outputs have the same value
    - the output value belongs to the set of possible denominations 
        (denominations are fixed in Dash)
    
Interaction A is done by looking at whether users who received money from a Phase 2 transaction,
where Dash is the curOut, peformed a coinjoin right after. This function uses the results 
from phase 2, checks the transaction labelled as the Dash transaction, checks if it has been 
spent, and if so, whether the spent transactions output follows the rules for a coinjoin. 

Interaction B is found by looking for transactions that had been obtained from a coinjoin. 
This looks at Phase 1 transactions, where Dash is a curIn, and if the transaction inputs  
were originally from the output of a coinjoin. Thus this will cycle through all inputs, 
finding if their spent transaction was a type of coinjoin. 

Requires blocksci data

'''
import csv
import blocksci
import pickle

# These denominations are 0.01 Dash, 0.1 DASH, 1 DASH and 10 DASH –
# https://docs.dash.org/en/latest/introduction/features.html#privatesend
denominations = [ 1000000,  # 0.01
                  1000010,     # same but with fee
                  10000000,  # 0.1
                  10000100,
                  100000000,  # 1
                  100001000,
                  1000000000,
                  1000010000] # 10

'''
This method tags transactions that were sent by ShapeShift and had been used in a coinjoin
Parameters
    chain : blocksci dash blockchain object
    dashp2: a list of dash phase 2 files in the format
`              {
                    'shapeshift tx index': [blockchain tx id..],
                    ...
                }
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
    denominations: a list of dash denominations to search for
    
'''
def interactionA(chain, dashp2, transactions, denominations):
    spentSSTxsCJ = []
    spentindexes = []
    tempcount = 0
    totalvalue = 0
    totaljoinedvalue  = 0
    skipped=0
    numspent=0
    for ssindex in dashp2:
        tempcount += 1
        if tempcount % 5000 == 0:
            print(str(tempcount) + "/" + str(len(dashp2)))
        if len(dashp2[ssindex]) == 0:
            continue
        for txv in dashp2[ssindex]:
            if txv['status'] != 'complete':
                continue
            hashx = txv['transaction']
            try:
                tx = chain.tx_with_hash(hashx)
            except RuntimeError:
                skipped+=1
                continue
            # compute exchange value of ss tx
            if 'outgoingCoin' not in txv:
                skipped+=1
                continue
            zecValue = int(float(txv['outgoingCoin'])*1e8)
            totalvalue += zecValue
            # find the output
            for out in tx.outs:
                # see if it was spent
                if  zecValue == out.value and out.is_spent:
                    # if spent, check if it went to a coinjoin
                    numspent+=1
                    spentTxIndex = out.spending_tx_index
                    spentTx = chain.tx_with_index(spentTxIndex)
                    if spentTxIndex in spentindexes:
                        continue
                    else:
                        spentindexes.append(spentTxIndex)
                    # if coinjoin, checks if inputs values were same
                    if len(spentTx.ins) > 2 and \
                       len(spentTx.outs) > 2 and \
                            set(spentTx.outs.value).intersection(set(denominations)):
                        print(spentTx.outs.value)
                        spentSSTxsCJ.append({'shapeshift_tx': ssindex, 'amount': zecValue,
                                                  'coinjoinTx': spentTx,
                                             'OGblockscitx':tx})
                        totaljoinedvalue += zecValue
    print('# of one hits ')
    print(len([x for x in dashp2 if len(dashp2[x])>0]))
    print('total val of one hits ')
    print(totalvalue)
    print('# of coinjoins')
    print(len(spentSSTxsCJ))
    print('val of coinjoins')
    print(totaljoinedvalue)
    print('skipped')
    print(skipped)


# spentTx.outs.value.min() == spentTx.outs.value.max() and \

'''
This method tags transactions that were received by ShapeShift and had inputs from coinjoins
Parameters
    chain : blocksci dash blockchain object
    dashp1: a list of dash phase 1 files in the format
`              {
                    'shapeshift tx index': [blockchain tx id..],
                    ...
                }
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
    denominations: a list of dash denominations to search for
'''
def interactionB(chain, dashp1, transactions, denominations):
    dashp1 = pickle.load(open('dash_p1.pkl', 'rb'))
    spentSSTxsCJ = []
    spentindexes = []
    count = 0
    tempcount = 0
    totalvalue = 0
    totaljoinedvalue  = 0
    for ssindex in dashp1:
        tempcount += 1
        if tempcount % 5000 == 0:
            print(str(tempcount) + "/" + str(len(dashp1)))
        if len(dashp1[ssindex]) != 1:
            continue
        txindex = dashp1[ssindex][0]
        tx = chain.tx_with_index(txindex)
        if tx is None:
            print('didnt find')
            continue
        sstx = transactions[ssindex]
        if 'DASH' not in sstx[5]:
            print(0)

        # compute exchange value of ss tx
        zecValue = sstx[2]
        totalvalue += zecValue
        # find the output
        d = False
        for out in tx.outs:
            if d:
                continue
            # see if it was spent
            if out.value == int(zecValue*1e8):
                count += 1
                d = True
                for inx in tx.ins:
                    # get spending tx
                    spentTxIndex = inx.spent_tx_index
                    spentTx = chain.tx_with_index(spentTxIndex)
                    # if coinjoin, checks if inputs values were same
                    if len(spentTx.ins) > 2 and \
                       len(spentTx.outs) > 2 and \
                        spentTx.outs.value.min() ==  spentTx.outs.value.max() and \
                        spentTx.outs.value.min() in denominations:
                        spentSSTxsCJ.append({'shapeshift_tx': sstx, 'amount': zecValue,
                                                  'coinjoinTx': spentTx,
                                         'OGblockscitx':tx})
                        totaljoinedvalue += zecValue
                        break

    print('# of one hits ')
    print(len([x for x in dashp1 if len(dashp1[x])==1]))
    print('total val of one hits ')
    print(totalvalue)
    print('# of coinjoins')
    print(len(spentSSTxsCJ))
    print('val of coinjoins')
    print(totaljoinedvalue)



'''
This method tags transactions that were received by ShapeShift and had inputs from coinjoins
Parameters
    chain : blocksci dash blockchain object
    dashp1: a list of dash phase 1 files in the format
`              {
                    'shapeshift tx index': [blockchain tx id..],
                    ...
                }
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
    denominations: a list of dash denominations to search for
'''
def interactionBNEWDATA(chain, dashp1, transactions, denominations):
    spentSSTxsCJ = []
    spentindexes = []
    count = 0
    tempcount = 0
    totalvalue = 0
    totaljoinedvalue  = 0
    for ssindex in dashp1:
        tempcount += 1
        if tempcount % 5000 == 0:
            print(str(tempcount) + "/" + str(len(dashp1)))
        if len(dashp1[ssindex]) == 0:
            continue
        for b in dashp1[ssindex]:
            txindex = b
            tx = chain.tx_with_index(txindex)
            if tx is None:
                print('didnt find')
                continue
            sstx = transactions[ssindex]
            if 'DASH' not in sstx[1]:
                print(0)

            # compute exchange value of ss tx
            if sstx[0] > 15204592:
                zecValue = sstx[-1]
            else:
                zecValue = sstx[0]
            #print(zecValue)
            totalvalue += zecValue
            # find the output
            d = False
            for out in tx.outs:
                if d:
                    continue
                # see if it was spent
                if out.value == int(zecValue*1e8):
                    count += 1
                    d = True
                    for inx in tx.ins:
                        # get spending tx
                        spentTxIndex = inx.spent_tx_index
                        spentTx = chain.tx_with_index(spentTxIndex)
                        # if coinjoin, checks if inputs values were same
                        if len(spentTx.ins) > 2 and \
                           len(spentTx.outs) > 2 and \
                            spentTx.outs.value.min() ==  spentTx.outs.value.max() and \
                            spentTx.outs.value.min() in denominations:
                            spentSSTxsCJ.append({'shapeshift_tx': sstx, 'amount': zecValue,
                                                      'coinjoinTx': spentTx,
                                             'OGblockscitx':tx})
                            totaljoinedvalue += zecValue
                            break

    print('total val of one hits ')
    print(totalvalue)
    print('# of coinjoins')
    print(len(spentSSTxsCJ))
    print('val of coinjoins')
    print(totaljoinedvalue)