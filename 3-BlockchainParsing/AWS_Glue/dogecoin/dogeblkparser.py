__author__ = 'haaroon'
import os
import pickle
from blockchain_parser.blockchain import Blockchain

count = 0
for block in blockchain.get_ordered_blocks(os.path.expanduser('~/blocks/index'), end=2531531, cache='dogecoin.pkl'):
    count+= 1
    if count % 200000 == 0:
        print("height=%d block=%s" % (block.height, block.hash))


import csv
count = 0
blockchain = Blockchain(os.path.expanduser('~/blocks'))
print("creating csvs")
blk_fieldnames = ['blockhash','n_transactions']
if os.path.isfile('blocks.csv'):
    bk_csvfile = open('blocks.csv', 'a')
    bk_writer = csv.DictWriter(bk_csvfile, fieldnames=blk_fieldnames)
else:
    bk_csvfile = open('blocks.csv', 'w+')
    bk_writer = csv.DictWriter(bk_csvfile, fieldnames=blk_fieldnames)
    bk_writer.writeheader()
    bk_csvfile.flush()

tx_fieldnames = ['tx_hash', 'blockhash', 'time', 'n_inputs', 'n_outputs']
if os.path.isfile('transactions.csv'):
    tx_csvfile = open('transactions.csv', 'a')
    tx_writer = csv.DictWriter(tx_csvfile, fieldnames=tx_fieldnames)
else:
    tx_csvfile = open('transactions.csv', 'w+')
    tx_writer = csv.DictWriter(tx_csvfile, fieldnames=tx_fieldnames)
    tx_writer.writeheader()
    tx_csvfile.flush()

vin_fieldnames = ['txid', 'vout', 'prev_txid', 'address', 'value', 'coinbase']
if os.path.isfile('vin.csv'):
    vin_csvfile = open('vin.csv', 'a')
    vin_writer = csv.DictWriter(vin_csvfile, fieldnames=vin_fieldnames)
else:
    vin_csvfile = open('vin.csv', 'w+')
    vin_writer = csv.DictWriter(vin_csvfile, fieldnames=vin_fieldnames)
    vin_writer.writeheader()
    vin_csvfile.flush()

vout_fieldnames = ['txid', 'n', 'address', 'value']
if os.path.isfile('vout.csv'):
    vout_csvfile = open('vout.csv', 'a')
    vout_writer = csv.DictWriter(vout_csvfile, fieldnames=vout_fieldnames)
else:
    vout_csvfile = open('vout.csv', 'w+')
    vout_writer = csv.DictWriter(vout_csvfile, fieldnames=vout_fieldnames)
    vout_writer.writeheader()
    vout_csvfile.flush()

for block in blockchain.get_unordered_blocks():
    bk_writer.writerow(
        {
         'blockhash': block.hash,
         'n_transactions': block.n_transactions,
        }
    )
    # for tx in block.transactions:
    #     for no, output in enumerate(tx.outputs):
    #         print("tx=%s outputno=%d type=%s value=%s" % (tx.hash, no, output.type, output.value))
    #         print(output.addresses)
    # write script to dump it

    # write transactions
    print("Writing txs")
    for tx in block.transactions:
        row = {
            'tx_hash': tx.hash,
            'blockhash': block.hash,
            'time': '-1',
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
                    'coinbase': vinx['coinbase']
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
                    'txid': tx['hash'],
                    'vout': vinx['vout'],
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