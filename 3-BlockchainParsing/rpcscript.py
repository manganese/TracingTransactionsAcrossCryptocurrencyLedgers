__author__ = 'haaroony'
'''
This script is a library which can be used to interface with Bitcoin and Bitcoin-forked 
blockchain nodes. Primarily here is it used to dump the transactions and blocks
into CSV files. To do so, please ensure that tha rpcuser, rpcpassword, rpcport, and url
variables are correct. 
'''
import os
import pandas as pd
import csv
import time
import requests
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import sys
from socket import error as socket_error

rpcuser = "USERNAME"
rpcpassword = "RPCPASSWORD"
rpcport = 0 # PORT NUMBER
url = "127.0.0.1"



def rpcConnection():
    '''
    Tests RPC via Auth Service Proxy
    :return:
    '''
    rpc_connection = AuthServiceProxy("http://%s:%s@%s:%i/" % (rpcuser, rpcpassword, url, rpcport), timeout=120)
    # test it
    count = 0
    maxTries = 5
    while(count<maxTries):
        count += 1
        try:
            info = rpc_connection.getblockchaininfo()
            return rpc_connection
        except JSONRPCException as e:
            print("Authentication error " + str(e))
            print("Exiting program")
            sys.exit(1)
        except Exception as e:
            # apologies for bad exception catching
            print("Socket error when connecting to rpc")
            print(e)
            print("Waiting 5 seconds then trying again")
            time.sleep(5)
    print("Could not establish a connection")
    print("Exiting")
    #sys.exit(1)


def customRpcCurlCommand(command, params=[]):
    '''
    runs a curl on the server and returns the results as json
    An example curl command we run would be
    curl --data-binary '{}' -H 'content-type:application/json;' http://USERNAME:PASSWORD@127.0.0.1:8332/
    :param command: command to run form the bitcoin rpc
    :param params: array of params, these are passed to the curl command
    :return:
    '''
    headers = {
        "content-type": "application/json"
    }
    jsonData = {
        "jsonrpc": "2.0",
        "id": "parser",
        "method": command,
        "params": params,
    }
    tries = 5
    count = 0
    while count <= tries:
        r = requests.post('http://'+rpcuser+':'+rpcpassword+"@"+url+':'+str(rpcport), headers=headers, json=jsonData)
        if r.json()['error'] != None:
            print("Got an error when running the commnd, \nError:")
            print(r.json()['error'])
            print("Waiting 5 seconds before trying again")
            print(command)
            print(params)
            time.sleep(5)
            count += 1
        else:
            return r.json()['result']
    if count == tries:
        print("Failed to execute command ("+command+") with params "+str(params)+" without an error")
        print("Could not execute without an error, quitting...")
        sys.exit(1)


def getBlocks(startblock=0, latestblock=2000):
    '''
    Parses block files from RPC into CSV and saves into CSV file blocks.csv
    :param startblock: start block height, int
    :param latestblock:  end block height, int. If set to 0 then gets latest height
    :return:
    '''
    # get the block data
    if latestblock == 0:
        latestblock = customRpcCurlCommand("getblockcount")
    # first in batch get all the blocks hashes
    print("Creating block csv file")
    blk_fieldnames = [ 'height', 'hash', 'n_tx', 'tx', 'time']
    block_csvfile = open('blocks.csv', 'w')
    blk_writer = csv.DictWriter(block_csvfile, fieldnames=blk_fieldnames)
    blk_writer.writeheader()
    block_csvfile.flush()
    count = 0
    print("Parsing heights")
    strblockheights = str(latestblock)
    for height in range(startblock, latestblock+1, 1):
        blockhash = customRpcCurlCommand("getblockhash", [height])
        block = customRpcCurlCommand('getblock', [blockhash])
        count += 1
        if count % 1000 == 0:
            print(str(count) + "/"+strblockheights)
            block_csvfile.flush()
        blk = {
            'height': block['height'],
            'hash': block['hash'],
            'n_tx': len(block['tx']),
            'tx': [tx for tx in block['tx']],
            'time': block['time']
        }
        blk_writer.writerow(blk)
    block_csvfile.flush()
    block_csvfile.close()
    # now get all the blocks
    print("Finish")


def getTransactions():
    '''
    Reads transactions fron blocks.csv and parses this into a transaction, vin and vout file.
    :return:
    '''
    txs = []
    print("reading block files")
    for block_chunk in pd.read_csv('blocks.csv', usecols=['tx'], chunksize=10000):
        blocks = block_chunk
        for row in blocks.itertuples():
            txs.extend(eval(row.tx))

        print("creating csvs")

            tx_fieldnames = ['tx_hash', 'blockhash', 'time', 'n_inputs', 'n_outputs']
            if os.path.isfile('transactions.csv'):
                tx_csvfile = open('transactions.csv', 'a')
                tx_writer = csv.DictWriter(tx_csvfile, fieldnames=tx_fieldnames)
            else:
                tx_csvfile = open('transactions.csv', 'w+')
                tx_writer = csv.DictWriter(tx_csvfile, fieldnames=tx_fieldnames)
                tx_writer.writeheader()
                tx_csvfile.flush()
            count = 0

            vin_fieldnames = [ 'txid', 'vout', 'prev_txid', 'address', 'value', 'coinbase']
            if os.path.isfile('vin.csv'):
                vin_csvfile = open('vin.csv', 'a')
                vin_writer = csv.DictWriter(vin_csvfile, fieldnames=vin_fieldnames)
            else:
                vin_csvfile = open('vin.csv', 'w+')
                vin_writer = csv.DictWriter(vin_csvfile, fieldnames=vin_fieldnames)
                vin_writer.writeheader()
                vin_csvfile.flush()

            vout_fieldnames = [ 'txid', 'n', 'address', 'value']
            if os.path.isfile('vout.csv'):
                vout_csvfile = open('vout.csv', 'a')
                vout_writer = csv.DictWriter(vout_csvfile, fieldnames=vout_fieldnames)
            else:
                vout_csvfile = open('vout.csv', 'w+')
                vout_writer = csv.DictWriter(vout_csvfile, fieldnames=vout_fieldnames)
                vout_writer.writeheader()
                vout_csvfile.flush()

            # write transactions
            print("Writing txs")
            for txhash in txs:
                count += 1
                if count % 1000 == 0:
                    print(str(count) + "/"+ str(len(txs)))
                    tx_csvfile.flush()
                tx = customRpcCurlCommand("getrawtransaction", [txhash, 1])
                row = {
                    'tx_hash': tx['hash'],
                    'blockhash': tx['blockhash'],
                    'time': tx['time'],
                    'n_inputs': len(tx['vin']),
                    'n_outputs': len(tx['vout']),
                }
                tx_writer.writerow(row)

                for voutx in tx['vout']:
                    address = []
                    if 'addresses' in voutx['scriptPubKey']:
                        address = voutx['scriptPubKey']['addresses']
                    vout = {
                        'txid': tx['hash'],
                        'n': voutx['n'],
                        'address': address,
                        'value': voutx['value'],
                    }
                    vout_writer.writerow(vout)
                    # utxo[tx['hash']+"_"+str(voutx['n'])] = {
                    #     'address': address,
                    #     'value': voutx['value'],
                    # }
                vout_csvfile.flush()


                # write vin
                for vinx in tx['vin']:
                    if 'coinbase' in vinx:
                        vin = {
                            'txid': tx['hash'],
                            'vout': -1,
                            'prev_txid': '',
                            'address': 'coinbase',
                            'value': 0,
                            'coinbase' : vinx['coinbase']
                        }
                    else:
                        # find = vinx['txid'] + "_" + str(vinx['vout'])
                        # if find in utxo:
                        #     vin = {
                        #         'txid': tx['hash'],
                        #         'vout': vinx['vout'],
                        #         'prev_txid': vinx['txid'],
                        #         'address': utxo[find]['address'],
                        #         'value': utxo[find]['value'],
                        #         'coinbase': '',
                        #     }
                        #     # utxo.pop(find)
                        # else:
                        vin = {
                            'txid':  tx['hash'],
                            'vout':  vinx['vout'],
                            'prev_txid': vinx['txid'],
                            'address': [],
                            'value': [],
                            'coinbase': '',
                        }
                    vin_writer.writerow(vin)
                vin_csvfile.flush()

        tx_csvfile.flush()
        tx_csvfile.close()
        vin_csvfile.close()
        vout_csvfile.close()
        # write vin
        # write vout
        print("end")


def restAPITxHash(hash):
    response = requests.get('http://'+url+':'+str(rpcport)+'/rest/tx/'+hash+'.json')
    if response.status_code==200:
        return response.json()
    else:
        print('error bad response '+str(response.status_code))
        return -1


def main():
    # Connect to RPC
    print("Checking rpc")
    rpc = rpcConnection()
    print("Getting block")
    # getBlocks(startblock=0,latestblock=2529065)
    print("Getting transactions")
    # getTransactions()
    print("")


if __name__ == '__main__':
    main()
