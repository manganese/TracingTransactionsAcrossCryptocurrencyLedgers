from argparse import ArgumentParser

__author__ = 'haaroony'
'''

 .d8888b. 888                              .d8888b. 888     d8b .d888888    
d88P  Y88b888                             d88P  Y88b888     Y8Pd88P" 888    
Y88b.     888                             Y88b.     888        888   888    
 "Y888b.  88888b.  8888b. 88888b.  .d88b.  "Y888b.  88888b. 888888888888888 
    "Y88b.888 "88b    "88b888 "88bd8P  Y8b    "Y88b.888 "88b888888   888    
      "888888  888.d888888888  88888888888      "888888  888888888   888    
Y88b  d88P888  888888  888888 d88PY8b.    Y88b  d88P888  888888888   Y88b.  
 "Y8888P" 888  888"Y88888888888P"  "Y8888  "Y8888P" 888  888888888    "Y888 
                          888                                               
                          888                                               
                          888      
Common Functions                       
'''

import blocksci
import csv
import numpy as np
import pandas as pd
import os
import datetime
from datetime import date, datetime, timedelta
import pickle

cpu_count = 1

def customdater(date):
    # use pass to drop errornous rows
    try:
        return datetime.utcfromtimestamp(int(float(date)))
    except:
        return np.nan


def filterTxByVoutVal(tx, val):
    '''
    Filters transactions by output value
    :param: tx: blocksci tx
    :param: val: value in int satoshis
    :return: True/False if one of the outputs had the same value
    '''
    for output in tx.outputs:
        if val == output.value:
            return True
    return False


def findMatchingTXesPhase1(chain, start, end, vout):
    '''
    Rapid transaction filtering using blocksci tools
    :param: chain : blocksci chain
    :param: start : int start block number
    :param: end   : int end block number
    :param: vout  : int value to filter outputs by 
    :return: list of blocksci transactions that match the above filters
    '''
    txes = chain.filter_txes(lambda tx: filterTxByVoutVal(tx, vout), start=start, end=end, cpu_count=cpu_count)
    return txes


def getBlockTimes(chain):
    '''
    Given a chain returns a sorted dict, timestamp:block
    :param chain: blocksci chain
    :return: dict {timestamp:chain}
    '''
    print("Finding block times")
    def blocktimefunc(b):
        # used as map function, returning tuples is faster
        return (b.timestamp, b.height)
    timeblocks = chain.map_blocks(blocktimefunc)
    timeblocksdict = {}
    for timeheighttuple in timeblocks:
        timeblocksdict[timeheighttuple[0]] = timeheighttuple[1]
    print("Block times found")
    return timeblocksdict


def blocktimefilter(blocktimes, timestamp, ahead, before):
    '''
    Filters block numbers based on given time stamp
    :param: blocktimes: dict of blocktimes blocknumber:timestamp
    :param: timestamp : int unix timestamp to find blocktimes after this time
    :param: ahead : int, number of block to add ahead
    :param: before: int, number of blocks to add before
    :returns: start , int start block number
              end   , int end   block number
    '''
    positions = [b for b in blocktimes.keys() if b > timestamp]
    if len(positions) == 0:
        print("No block heights found for this timestamp")
        print("Likely the chain is not that far")
        return -1, -1
    block = blocktimes[positions[0]]
    start = block - 1 - before
    end = block + ahead
    if start < 0:
        start = 0
    return start, end


def convertAmount(amount):
    '''
    Converts BTC to satoshis
    :param: amount, int amount
    :return: amount*1e8 in int. 
    '''
    return int(amount*100000000)


def findSimilarTxPhase1(chain='', sstxes='', blocks_ahead=3, blocks_before=1, blocktimes=[]):
    '''
    Finds transactions which are similar to the sstxes in the blockchain
    :param: chain, blocksci chain
    :param: sstxes, list of shapeshift transactions to investigate
    :param: blocks_ahead, number of blocks to look ahead, this is factored in per timestamp of the shapeshift transaction
    :param: blocks_before, same as above but blocks beforee
    :param: blocktimes, list of blocktimes 
    :return: list of dict of transactions found that match, per shapeshift transaction
    '''
    print("Phase 1: Finding similar transactions")
    if chain is '' or sstxes is '':
        print('Error with chain or sstxes item')
        raise ValueError('bad variable in findSimilarTx, chain or sstxes is empty, please check arguments')
    foundTXs = []
    # get list of blocks and times
    if blocktimes == []:
        blocktimes = getBlockTimes(chain)
    count = 0
    for sstx in sstxes.itertuples():
        if count % 500 == 0:
            print("Processed %i/%i" % (count, len(sstxes)))
        count += 1
        # get the time ahead and behind
        startblock, endblock = blocktimefilter(blocktimes, sstx.SS_Timestamp, blocks_ahead, blocks_before)
        possibleTXs = []
        if startblock == -1 and endblock == -1:
            print("Skipping tx, timestamp not in chain")
            continue
        else:
            amount = convertAmount(sstx.Value)
            possibleTXs = findMatchingTXesPhase1(chain, startblock, endblock, amount)
        # search for a transaction whtin this timestamp and value in the blockchain
        res = {
            'shapeshift_tx' : sstx,
            'possible_txs': possibleTXs
        }
        foundTXs.append(res)
    return foundTXs


def phase2filterTxByVoutVal(tx, lower, upper):
    '''
    Filters transactions by checking if any of their output is within the lower-upper range
    :param: tx, blocksci transaction
    :param: lower, int, lower bound output value to search for, in satoshis
    :param: upper, int, upper bound output value to search for, in satoshis
    :return: True if successful, else False
    '''
    for out in tx.outputs:
        if lower <= out.value <= upper:
            return True


def findMatchingTXesPhase2(chain, startblock, endblock, vout, percent):
    '''
    Filters transactions from those on chain
    :param: chain, blocksci chain
    :param: startblock, int, block number to start from
    :param: endblock, int, block number to end searching
    :param: vout, int output value to search for
    :param: percent, percetange error
    :return: txes, list of transactions found
    '''
    lower = vout * (1.00 - percent) * 100000000
    upper = vout * (1.00 + percent) * 100000000
    txes = chain.filter_txes(lambda tx: phase2filterTxByVoutVal(tx, lower, upper), start=startblock, end=endblock, cpu_count=cpu_count)
    txes = list(set(txes))
    # print("Transactions found %i " % len(txes))
    return txes


def calculateResult(value, fee, rate):
    '''
    Calculate the value below, self-explanatory
    '''
    return ((value * rate) - fee)


def findSimilarTxPhase2(chain='', sstxes='', blocks_ahead=4, blocks_before=0, percent=0.01, blocktimes=[]):
    '''
    Find similar transactions for phase 2
    This is similar to findSimilarTxPhase1, see the documentation for that
    '''
    print("Phase 2: Finding similar transactions")
    if chain is '' or sstxes is '':
        print('Error with chain or sstxes item')
        raise ValueError('bad variable in findSimilarTxPhase2, chain or sstxes is empty, please check arguments')
    foundTXs = []
    # get list of blocks and times
    if blocktimes == []:
        blocktimes = getBlockTimes(chain)
    count = 0
    for sstx in sstxes.itertuples():
        if count % 5000 == 0:
            print("Processed %i/%i" % (count, len(sstxes)))
        count += 1
        # get the time ahead and behind
        startblock, endblock = blocktimefilter(blocktimes, sstx.SS_Timestamp, blocks_ahead, blocks_before)
        # search for a transaction whtin this timestamp and value in the blockchain
        value = calculateResult(sstx.Value, sstx.Miner_Fee, sstx.Rate)
        possibleTXs = findMatchingTXesPhase2(chain, startblock, endblock, value, percent)
        res = {
            'shapeshift_tx' : sstx,
            'possible_txs': possibleTXs
        }
        foundTXs.append(res)
    return foundTXs


def analyze(txs):
    '''
    Given a list of transactions, analyses them to see how many hits were found
    '''
    print("Analyzed %i txs" % len(txs))
    totalhits = 0
    onehit = 0
    twohits = 0
    morethan = 0
    for tx in txs:
        if len(tx['possible_txs']) > 0:
            totalhits += 1
            if len(tx['possible_txs']) == 1:
                onehit += 1
            elif len(tx['possible_txs']) == 2:
                twohits += 1
            else:
                morethan += 1
    print("Total Hits found %i/%i" % (totalhits, len(txs)))
    print("Hits == 0 : %i/%i" % ((len(txs)-totalhits), len(txs)))
    print("Hits == 1 : %i/%i" % (onehit, len(txs)))
    print("Hits == 2 : %i/%i" % (twohits, len(txs)))
    print("Hits  > 2 : %i/%i" % (morethan, len(txs)))
    return totalhits, onehit, twohits, morethan


def dump(txs, path, name):
    '''
    Saves transactions to a pickle file
    :param: txs, list of transactions
    :param: path, path to save the file
    :param: name, file name to save
    :return: Nothing
    '''
    print('Pickling results to %s' % str(path+'txs_'+name+'.pkl'))
    pickle.dump(txs, open(path+'txs_'+name+'.pkl'))
    print('Complete')


def loadShapeShiftRates(path='', curOut='', curIn=''):
    '''
    Load shapeshift rates from a file
    :param: path, string of the full file path
    :param: curOut, string, of the curout to sort by
    :param: curIn, string of the curIn to sort by
    :return: dataframe of rates
    '''
    # return rates tranactions
    df = pd.read_csv(path, header=0, error_bad_lines=False, skip_blank_lines = True, memory_map = True)
    if curOut != '':
        df = df[df['Pair'].str.contains('_'+curOut)]
    else:
        df = df[df['Pair'].str.contains(curIn + '_')]
    df = df.dropna()
    return df


def getSSAddresses(txs):
    '''
    Given a list of transactions, it extracts the shapeshift address from the outputs and returns these
    :param: txs, list of transactions
    :return: list of addressess
    '''
    onehits = [x for x in txs if len(x['possible_txs'])==1]
    addresses = set([])
    for x in onehits:
        val = convertAmount(x['shapeshift_tx'].amount)
        temp = [y.address for y in x['possible_txs'][0].outs if y.value == val][0].address_string
        addresses.add(temp)
    return list(addresses)


def dumpToCsv(ssAddresses, filename):
    '''
    Saves a list addresses to a csv
    :param: ssAddresses, list of addresses
    :param: filename, full file path to save
    :return: Nothing
    '''
    df = pd.DataFrame(ssAddresses, columns=['address'])
    df.to_csv(filename, index=False)


def findTheOptimum(ss_data, rates, chain, curIn, before, after, rangex):
    curOut = curIn
    print("Finding the optimum value")
    sstx = loadShapeShiftRates(path=ss_data, curIn=curIn)
    # use a small range to test
    sstx = sstx[:rangex]
    phase1Results = { 'ahead': {}, 'before': {}}
    blocktimes = getBlockTimes(chain)
    for i in range(1, after, 1):
        tx = findSimilarTxPhase1(chain=chain, sstxes=sstx, blocks_ahead=i, blocks_before=0, blocktimes=blocktimes)
        totalhits, onehit, twohits, morethan = analyze(tx)
        phase1Results['ahead'][i] = {
            'totalhits': totalhits,
            'onehit': onehit,
            'twohits': twohits,
            'morethan': morethan,
        }
        print(phase1Results)

    for i in range(0, before, 1):
        tx = findSimilarTxPhase1(chain=chain, sstxes=sstx, blocks_ahead=1, blocks_before=i,blocktimes=blocktimes)
        totalhits, onehit, twohits, morethan = analyze(tx)
        phase1Results['before'][i] = {
            'totalhits': totalhits,
            'onehit': onehit,
            'twohits': twohits,
            'morethan': morethan,
        }
        print(phase1Results)

    phase2Results = {'ahead': {}, 'before': {}}
    sstx = loadShapeShiftRates(path=rates, curOut=curOut)
    percent = 0.01
    # use a small range to test
    sstx = sstx[:rangex]
    for i in range(0, after, 1):
        tx = findSimilarTxPhase2(chain=chain, sstxes=sstx, blocks_ahead=i, blocks_before=1, percent=percent, blocktimes=blocktimes)
        totalhits, onehit, twohits, morethan = analyze(tx)
        if percent not in phase2Results:
            phase2Results['ahead'][i] = {
                'totalhits': totalhits,
                'onehit': onehit,
                'twohits': twohits,
                'morethan': morethan,
            }

    for i in range(0, before, 1):
        tx = findSimilarTxPhase2(chain=chain, sstxes=sstx, blocks_ahead=1, blocks_before=i, percent=percent, blocktimes=blocktimes)
        totalhits, onehit, twohits, morethan = analyze(tx)
        if percent not in phase2Results:
            phase2Results['before'][i] = {
                'totalhits': totalhits,
                'onehit': onehit,
                'twohits': twohits,
                'morethan': morethan,
            }

    print(curIn)
    print("Phase 1 res")
    print(phase1Results)
    print("Phase 2 res")
    print(phase2Results)
    print("")
    return phase1Results, phase2Results


def getUTXOphase1(txs_phase1):
    '''
    extracts the transaction hash from spent shapeshift phase1 transactions
    :param: txs_phase1, list of shapeshift transactions
    :return: list of transaction hashes 
    '''
    utxoset = set([])
    onehittxs = [x for x in txs_phase1 if len(x['possible_txs']) == 1]
    # for each one hit get the exact txid, vout n pair
    for onehit in onehittxs:
        val = convertAmount(onehit['shapeshift_tx'].amount)
        for out in onehit['possible_txs'][0].outs:
            if out.value == val:
                utxoset.add(str(onehit['possible_txs'][0].hash))
                break
    return utxoset


def filterUTXO(txs_phase2, utxoset, percent):
    og_utxoset = utxoset.copy()
    removedutxoCount = {}
    for tx in txs_phase2:
        found = False
        for subtx in tx['possible_txs']:
            for input in subtx.inputs:
                if str(input.spent_tx.hash) in utxoset:
                    # print('f')
                    utxoset.remove(str(input.spent_tx.hash))
                    hits = len(tx['possible_txs'])
                    if hits in removedutxoCount:
                        removedutxoCount[hits] += 1
                    else:
                        removedutxoCount[hits] = 1
                found = True
                break
            if found:
                break
    print("Original utxoset %i, New utxo set %i" % (len(og_utxoset), len(utxoset)))
    print(removedutxoCount)
    return utxoset


def unspentSSUtxo():
    # Quick method for a test
    # load normal sstxs
    sstx_phase1 = loadShapeShiftRates(path='ShapeShift/', curIn='ZEC')
    # load preprocessed rates
    sstx_phase2 = loadShapeShiftRates(path='Results.csv', curOut='ZEC')
    chain = blocksci.Blockchain('BlockSciZcash')
    # Do phase 1 and get all the utxos for SS
    txs_phase1 = findSimilarTxPhase1(chain=chain, sstxes=sstx_phase1, blocks_ahead=3, blocks_before=1)
    utxoset = getUTXOphase1(txs_phase1)
    # Do phase 2
    txs_phase2 = findSimilarTxPhase2(chain=chain, sstxes=sstx_phase2, blocks_ahead=4, blocks_before=0, percent=0.01)
    # filter out spent utxos from single
    newutxoset = filterUTXO(txs_phase2, utxoset, 0.01)
    # check how many utxo are in 2 and more than 2, use them
    # see size of utxo set


def main():
    parser = ArgumentParser()
    parser.add_argument("-p", "--phase", dest="phase_type", type=int,
                        help="if 1 use phase 1, if 2 use phase 2",
                        default=1)
    parser.add_argument("-ci", "--cur_in", dest="cur_in", type=str,
                        help="Cur In to find, ignore if using cur out",
                        default="")
    parser.add_argument("-co", "--cur_out", dest="cur_out", type=str,
                        help="Cur Out to find, ignore if using cur in",
                        default="")
    parser.add_argument("-sd", "--ss-data-dir", dest="ss_data",
                        required=True, type=str,
                        help="location of shapeshift data")
    parser.add_argument("-bd", "--blocksci_data_dir", dest="blocksci_data",
                        required=True, type=str,
                        help="location of blocksci data file, must correspond "
                             "to cur in or cur out")
    parser.add_argument("-d", "--dump_path", dest="dump_path",
                        type=str, help="path to dump data", default="")
    parser.add_argument("-ba", "--blocks_ahead", dest="blocks_ahead", default=3,
                        type=int, help="maximum blocks to look ahead for transaction")
    parser.add_argument("-bb", "--blocks_before", dest="blocks_before", default=0,
                        type=int, help="maximum blocks to look before for transaction")

    args = parser.parse_args()
    blocksci_data = args.blocksci_data
    ss_data = args.ss_data
    phase = 1

    percent = 0.01

    curIn = ''
    curOut = ''
    dump_path = ''
    if args.cur_in != '':
        curIn = args.cur_in
    else:
        curOut = args.cur_out

    if args.dump_path != '':
        dump_path = args.dump_path

    blocks_ahead = 3
    blocks_before = 0
    if args.blocks_ahead != 3:
        blocks_ahead = args.blocks_ahead

    if args.blocks_before != 0:
        blocks_before = args.blocks_before

    print("Loading all the ShapeShift Transactions")
    if curIn != '':
        # load normal sstxs
        sstx = loadShapeShiftRates(path=ss_data, curIn=curIn)
    else:
        # load preprocessed rates
        sstx = loadShapeShiftRates(path=ss_data, curOut=curOut)
    print("Initialising blockchain")
    print("Creating a chain object")
    chain = blocksci.Blockchain(blocksci_data)
    if phase == 1:
        txs = findSimilarTxPhase1(chain=chain, sstxes=sstx, blocks_ahead=blocks_ahead, blocks_before=blocks_before)
        print("Getting addresses")
        ssAddresses = getSSAddresses(txs)
        print("Dumping to csv")
        dumpToCsv(ssAddresses, 'phase1addresses.csv')
        print("Done")
    else:
        txs = findSimilarTxPhase2(chain=chain, sstxes=sstx, blocks_ahead=blocks_ahead, blocks_before=blocks_before, percent=percent)

    analyze(txs)
    if dump_path != '':
        dump(txs, dump_path, curIn+curOut+'phase'+str(phase))


if __name__ == '__main__':
    main()
