__author__ = 'haaroon'
'''


'''
import pickle
import pandas
import requests
import plotly.graph_objs as go
import plotly
import numpy as np


def getSentETHAddress(address):
    '''
    Uses the Etherscan API to obtain all transactions that a given address sent
    :param address: ETH addrtess
    :return: list of transactions and addresses
    '''
    etherscanapi = '4X2224PGP9JIQXX611W8MIKTIKWW821SD4'
    ethergetA = 'http://api.etherscan.io/api?module=account&action=txlist&address='
    ethergetB = '&startblock=0&endblock=99999999&sort=asc&apikey=' + etherscanapi
    response = requests.get(ethergetA + address + ethergetB)
    if response.json()['status'] != '1':
        print('bad response ' + address)
        print(response.status_code)
        print(response.text)
        return False
    addresses = []
    for tx in response.json()['result']:
        if tx['to'] == address:
            continue
        else:
            addresses.append(tx)

    ethergetAinternal = 'http://api.etherscan.io/api?module=account&action=txlistinternal&address='
    ethergetBinternal = '&startblock=0&endblock=2702578&sort=asc&apikey=' + etherscanapi
    response = requests.get(ethergetA + address + ethergetB)
    if response.json()['status'] != '1':
        print('bad response ' + address)
        print(response.status_code)
        print(response.text)
    else:
        for tx in response.json()['result']:
            if tx['to'] == address:
                continue
            else:
                addresses.append(tx)
    return addresses




def main():
    starscapetxs = pickle.load(open('monero_starscape.pkl', 'rb'))
    sstimes = getSentETHAddress('0xBA9e83D6eF2fb1c189a087C1Ea86065AE0143e10')
    shapeshiftaddresses = []
    starscape_outgoing = {}
    starscape_xmrout_time = []
    for a in starscapetxs:
        if a['outgoingType'] == 'XMR':
            shapeshiftaddresses.append((a['address'], a['incomingCoin'] * 1e18))
            starscape_outgoing[(a['address'], a['incomingCoin'] * 1e18)] = a['outgoingCoin']
    sstxes = []
    for tx in sstimes:
        if (tx['to'], int(tx['value'])) in shapeshiftaddresses:
            sstxes.append([int(tx['timeStamp']), int(tx['value']) / 1e18])
        if (tx['to'], int(tx['value'])) in starscape_outgoing:
            a = [int(tx['timeStamp']), starscape_outgoing[(tx['to'], int(tx['value']))]]
            starscape_xmrout_time.append(a)
    timestamps = [x[0] for x in sstxes]
    mintimestamp = 1516406400  # min(timestamps)
    maxtimestamp = 1517097600  # max(timestamps)
    xmrss = pandas.read_csv('xmrss.csv')
    xmrtxes = []
    for x in xmrss.iterrows():
        if x[1]['timestamp'] > mintimestamp and x[1]['timestamp'] < maxtimestamp:
            xmrtxes.append((x[1]['timestamp'], x[1]['amount']))
    starscapes_trace = go.Scatter(
        x=[x[0] for x in starscape_xmrout_time],
        y=[x[1] for x in starscape_xmrout_time],
        mode='markers',
        name='starscapes',
        fillcolor='red'
    )
    ssxmrtxes_trace = go.Scatter(
        x=[x[0] for x in xmrtxes],
        y=[x[1] for x in xmrtxes],
        mode='markers',
        name='ss_curin_xmr',
        fillcolor='black'
    )
    plotly.offline.plot({
        "data": [starscapes_trace, ssxmrtxes_trace],
        "layout": go.Layout(title="hello world")
    }, auto_open=True)

    xmrss = xmrss.drop(['txid', 'Unnamed: 0'], axis=1).drop_duplicates()
    for strval in starscape_xmrout_time:
        intval = float(strval[1])
        if len(xmrss[((intval * 0.99) <= xmrss.amount) & (xmrss.amount <= intval)]):
            print()
            print(intval)
            print(len(xmrss[((intval * 0.99) <= xmrss.amount) & (xmrss.amount <= intval)]))


if __name__ == '__main__':
    main()
