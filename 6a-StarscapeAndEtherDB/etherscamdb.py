__author__ = 'haaroon'
'''
This code finds etherscamdb addresses their transactions and whether or not they sent funds to ShapeShift. 
'''
import requests
import time
import pickle

etherscanapi = 'APIKEY'


def checkss(addr):
    '''
    Takes an address, check if it belongs to shapeshift, if so return json result of the tx, else returns a negative integer
    :param addr: cryptocurrency address as string
    :return: json if success, negative integer if error
    '''
    r = requests.get('https://shapeshift.io/txstat/'+addr)
    if r.status_code!=200:
        return -1
    if r.json()['status'] == 'error':
        #print('no - '+addr+' '+r.json()['error'])
        return -3
    else:
        #print('SS ADDR '+addr)
        return r.json()


def getEthAddresses(address):
    '''
    Gets details of sent txs from a list of eth addresses
    :param address: list of eth addresses as string
    :return: results per address
    '''
    time.sleep(1)
    addrs = []
    # 1 hop
    result = getSentETHAddress(address)
    if result == False:
        return []
    for address in result:
        addrs.append(address)
    addrs = list(set(addrs))
    return addrs


def getSentETHAddress(address):
    '''
    Given an address, using etherscan.io to obtain the transactions it sent
    :param address: eth address as str
    :return: details of its transactions
    '''
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
    print('Getting scammer addresses')
    scamlist = requests.get('https://etherscamdb.info/api/addresses/')
    print('Parsing the categories')
    categories = {}
    for scam in scamlist.json()['result']:
        cat = scamlist.json()['result'][scam]['category']
        if cat in categories:
            categories[cat] += 1
        else:
            categories[cat]=1
    # e.g. { 'Fake ICO': 5, 'Phishing': 516, 'Scam': 1, 'Scamming': 1356 }
    print('Finding the coins')
    coins = {}
    for scam in scamlist.json()['result']:
        cat = scamlist.json()['result'][scam]['coin']
        if cat in coins:
            coins[cat] += 1
        else:
            coins[cat]=1
    addrs = set(scamlist.json()['result'].keys())
    validtxs = txs.where(txs.from_address.isin(addrs)).collect()
    validtxs2 = {}
    for row in validtxs:
        if row.from_address not in validtxs2:
            validtxs2[row.from_address] = []
        validtxs2[row.from_address].append(row)
    validtxs = validtxs2
    del validtxs2
    sstxes = []
    count = 0

    print('Checking if any belonged to shapeshift')
    for scam in scamlist.json()['result']:
        print(str(count) + '/1878')
        scamval=scamlist.json()['result'][scam]
        count += 1
        sentEthAddrs = []
        for addr in scamval['addresses']:
            if addr in validtxs:
                for row in validtxs[addr]:
                    sentEthAddrs.append(row.to_address)
        sentEthAddrs = list(set(sentEthAddrs))
        print('Found ' + str(len(sentEthAddrs)) + ' interacted addresses')
        scams = {}
        for addr in sentEthAddrs:
            v = checkss(str(addr))
            if v:
                scams[addr] = v
        if len(scams):
            scamval['scams'] = scams
            sstxes.append(scamval)
        print('found ' + str(len(scams)) + ' SS addresses')
    print('Dumping to file called scams2.pkl')
    pickle.dump(sstxes, open('scams2.pkl', 'wb'))

    print('Running some analysis')
    # Analysis
    # status
    status={}
    for scam in sstxes:
        for s in scam['scams']:
            stat = scam['scams'][s]['status']
            if stat in status:
                status[stat]+=1
            else:
                status[stat]=1

    ## Success and failure?
    print('Did any scams succeed or fail?')
    success = 0
    failure = 0
    total = 0
    totalfailure = 0
    equalfailandscam = 0
    moresuccess = 0
    morefailure = 0
    for tx in sstxes:
        f = 0
        sc = 0
        for s in tx['scams']:
            total += 1
            if tx['scams'][s]['status'] == 'failed':
                failure+=1
                f+=1
            elif tx['scams'][s]['status']=='complete':
                success+=1
                sc+=1
        if f == len(tx['scams']):
            totalfailure += 1
            print(tx)
            print()
        if f == sc:
            equalfailandscam +=1
        if f < sc:
            moresuccess += 1
        if sc < f:
            morefailure +=1

    print('obtaning transactions that were success')
    success=[]
    for scam in sstxes:
        for s in scam['scams']:
            if scam['scams'][s]['status']=='complete':
                success.append(scam)
                break

    print('most common curout & total value of curouts')
    curin = {}
    curout = {}
    btc=[]
    for scam in success:
        for s in scam['scams']:
            if scam['scams'][s]['status'] == 'complete':
                ci = scam['scams'][s]['incomingType']
                co = scam['scams'][s]['outgoingType']
                if co == 'BTC':
                    btc.append(scam['scams'][s])
                if ci in curin:
                    curin[ci]['count']+=1
                    curin[ci]['value'] += float(scam['scams'][s]['incomingCoin'])
                else:
                    curin[ci] = {}
                    curin[ci]['count'] = 1
                    curin[ci]['value'] = float(scam['scams'][s]['incomingCoin'])
                if co in curout:
                    curout[co]['count'] = 1
                    curout[co]['value'] += float(scam['scams'][s]['incomingCoin'])
                else:
                    curout[co] = {}
                    curout[co]['count'] = 1
                    curout[co]['value'] = float(scam['scams'][s]['incomingCoin'])

    pprint(curin)
    print()
    pprint(curout)

    print('sub category count')
    subcat = {}
    for scam in success:
        for s in scam['scams']:
            if scam['scams'][s]['status'] == 'complete':
                inc = float(scam['scams'][s]['incomingCoin'])
                cat = scam['category']
                if cat in subcat:
                    subcat[cat]['count'] += 1
                    subcat[cat]['value'] += inc
                else:
                    subcat[cat] = {}
                    subcat[cat]['count'] = 1
                    subcat[cat]['value'] = inc
                    subcat[cat]['subcategory'] = {}

                if 'subcategory' in scam:
                    smolcat = scam['subcategory']
                    if smolcat in subcat[cat]['subcategory']:
                        subcat[cat]['subcategory'][smolcat]['count'] +=1
                        subcat[cat]['subcategory'][smolcat]['value'] += inc

                    else:
                        subcat[cat]['subcategory'][smolcat] = {}
                        subcat[cat]['subcategory'][smolcat]['count'] = 1
                        subcat[cat]['subcategory'][smolcat]['value'] = inc
    pprint(subcat)
    print()


    print('trust-scam values')
    ot = {}
    val = 0
    for scam in success:
        for s in scam['scams']:
            if scam['scams'][s]['status'] == 'complete' and 'subcategory' in scam:
                if scam['subcategory'] == 'Trust-trading' or scam['subcategory']=='Trust-Trading':
                    val += float(scam['scams'][s]['incomingCoin'])
                    otx = scam['scams'][s]['outgoingType']
                    if otx in ot:
                        ot[otx] +=  float(scam['scams'][s]['incomingCoin'])
                    else:
                        ot[otx] =  float(scam['scams'][s]['incomingCoin'])
    print(' -> myetherwallet values')
    ot = {}
    val = 0
    for scam in success:
        for s in scam['scams']:
            if scam['scams'][s]['status'] == 'complete' and 'subcategory' in scam:
                if scam['subcategory'] == 'MyEtherWallet':
                    val += float(scam['scams'][s]['incomingCoin'])
                    otx = scam['scams'][s]['outgoingType']
                    if otx in ot:
                        ot[otx] +=  float(scam['scams'][s]['incomingCoin'])
                    else:
                        ot[otx] =  float(scam['scams'][s]['incomingCoin'])


    print('Counting Filures')
    for scam in sstxes:
        cf = False
        for s in scam['scams']:
            if scam['scams'][s]['status'] != 'failed':
                cf = True
                break
        if not cf:
                pprint(scam)


    print('Looking for totals of the larger scams')
    for a in bigscams:
        print(a['name'])
        total = {}
        for s in a['scams']:
            if a['scams'][s]['status'] != 'failed':
                if a['scams'][s]['incomingType'] in total:
                    total[a['scams'][s]['incomingType']] += a['scams'][s]['incomingCoin']
                else:
                    total[a['scams'][s]['incomingType']] = a['scams'][s]['incomingCoin']
        print(total)

    scams = pickle.load(open('scams2.pkl','rb'))
    success=[]
    for scam in sstxes:
        for s in scam['scams']:
            if scam['scams'][s]['status']=='complete':
                success.append(scam)
                break
    print('most common curout & total value of curouts')
    btc=[]
    for i,scam in enumerate(success):
        for s in scam['scams']:
            if scam['scams'][s]['status'] == 'complete':
                co = scam['scams'][s]['outgoingType']
                if co == 'BTC':
                    btc.append((i,scam['scams'][s],[]))
    print(btc)
    scams = pickle.load(open('scams2.pkl','rb'))
    success=[]
    for scam in sstxes:
        for s in scam['scams']:
            if scam['scams'][s]['status']=='complete':
                success.append(scam)
                break

    ## most common curout & total value of curouts
    t=0
    utxouturns = {}
    for i,scam in enumerate(success):
        print(str(i)+'/'+str(len(success)))
        for s in scam['scams']:
            if scam['scams'][s]['status'] == 'complete':
                co = scam['scams'][s]['outgoingType']
                if co == 'BTC':
                    withdrawaddr = scam['scams'][s]['withdraw']
                    tx = chain.tx_with_hash(scam['scams'][s]['transaction'])
                    for outtx in tx.outs:
                        if outtx.address.address_string == withdrawaddr:
                            if outtx.is_spent:
                                spenttx = outtx.spending_tx
                                # check if utxo based?
                                for out2 in spenttx.outs:
                                    res = checkss(out2.address.address_string)
                                    if res == -1:
                                        print('bad status code')
                                    elif res == -2:
                                        print('exception??')
                                    elif res == -3:
                                        pass
                                    else:
                                        if i in utxouturns:
                                            utxouturns[i].append(res)
                                        else:
                                            utxouturns[i]=[res]

    print('scam description, total scammed out to BTC, total UTXO uturns based')
    totalbtc = 0
    for s in utxouturns:
        print(s)
        scam = success[s]
        allcuroutaddrs = []
        allcuroutaddrs.extend(success[s]['addresses'])
        print(scam['description'])
        totalbtcscam = 0.0
        for s2 in scam['scams']:
            if scam['scams'][s2]['status']=='failed':
                continue
            allcuroutaddrs.append(scam['scams'][s2]['withdraw'])
            if scam['scams'][s2]['outgoingType']=='BTC':
                totalbtcscam+=float(scam['scams'][s2]['outgoingCoin'])
        print('total scammed to X-BTC: '+ str(totalbtcscam))
        scammedback = 0.0
        curouts = {}
        curoutaddrs = []
        for s2 in utxouturns[s]:
            if s2['status']=='failed':
                continue
            scammedback += s2['incomingCoin']
            co = s2['outgoingType']
            curoutaddrs.append(s2['withdraw'])
            if co in curouts:
                curouts[co]+=1
            else:
                curouts[co]=1
        for newcuroutaddr in curoutaddrs:
            if newcuroutaddr in allcuroutaddrs:
                print('returned to OG')
        print('total UTXO Scammed back: ' +str(scammedback))
        print('percentage :' + str(scammedback/totalbtcscam*100) + '%')
        print('curouts ' + str(co))
        print()
        totalbtc+=scammedback
    print(totalbtc)


if __name__ == '__main__':
    main()