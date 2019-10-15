__author__ = 'haaroon'
from pyspark.sql.types import *

def convertblockscript():
    # write header
    blk_fieldnames = [ 'height', 'hash', 'n_tx', 'tx', 'time']
    block_csvfile = open('blocks_new.csv', 'w')
    blk_writer = csv.DictWriter(block_csvfile, delimiter=';', fieldnames=blk_fieldnames,)
    blk_writer.writeheader()
    block_csvfile.flush()
    import pandas as pd
    count = 0
    for block_chunk in pd.read_csv('blocks.csv', chunksize=10000):
        print(str(count)+'/'+str(1546854))
        count+=10000
        buffer = []
        for b in block_chunk.iterrows():
            block = b[1].to_dict()
            block['tx'] = eval(block['tx'])
            buffer.append(block)
        blk_writer.writerows(buffer)

sql_sc = SQLContext(sc)

# blocks
# height,hash,n_tx,tx,time
# 0,12a765e31ffd4059bada1e25190f6e98c99d9714d334efa41a195a7e7e04bfe2,1,[u'97ddfbbae6be97fd6cdf3e7ca13232a3afff2353e29badfab7f73011edd4ced9'],1317972665

print('---blocks---')
schema = StructType([
    StructField("height", IntegerType(), True),
    StructField("hash", StringType(), True),
    StructField("n_tx", IntegerType(), True),
    StructField("tx", StringType(), True),
    StructField("time", IntegerType(), True)])

print('reading as rdd')
rdd = sc.textFile("blocks.csv").map(lambda line: line.split(";"))
print('applying schema')
df = sqlContext.createDataFrame(rdd, schema)
print('writing to parquet')
df.write.parquet('blocks.parquet')
print('done')
print('')

# transactions
print('---transactions---')
schema = StructType([
    StructField("tx_hash", StringType(), True),
    StructField("blockhash", StringType(), True),
    StructField("time", IntegerType(), True),
    StructField("n_inputs", IntegerType(), True),
    StructField("n_outputs", IntegerType(), True)])

print('reading as rdd')
rdd = sc.textFile("transactions.csv").map(lambda line: line.split(","))
print('applying schema')
df = sqlContext.createDataFrame(rdd, schema)
print('writing to parquet')
df.write.parquet('transactions-parquet')
print('done')
print('')


# vin

print('---vin---')
schema = StructType([
    StructField("txid", StringType(), True),
    StructField("vout", IntegerType(), True),
    StructField("prev_txid", StringType(), True),
    StructField("address", StringType(), True),
    StructField("value", StringType(), True),
    StructField("coinbase", StringType(), True)])

print('reading as rdd')
rdd = sc.textFile("vin.csv").map(lambda line: line.split(","))
print('applying schema')
df = sqlContext.createDataFrame(rdd, schema)
print('writing to parquet')
df.write.parquet('vin-parquet')
print('done')
print('')


# vout
print('---vout---')
schema = StructType([
    StructField("txid", StringType(), True),
    StructField("n", LongType(), True),
    StructField("address", StringType(), True),
    StructField("value", StringType(), True)])

print('reading as rdd')
rdd = sc.textFile("vout.csv").map(lambda line: line.split(";"))
print('applying schema')
df = sqlContext.createDataFrame(rdd, schema)
print('writing to parquet')
df.write.parquet('vout-parquet')
print('done')
print('')
