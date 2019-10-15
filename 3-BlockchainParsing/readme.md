##### Ethereum and Ethereum Classic

For Ethereum and Ethereum Classic, we ran the geth program as a local node,
allowing it to sync. Once synced we extracted the blocks and transactions into
csv files using the Etherem-ETL tool https://github.com/blockchain-etl/ethereum-etl.

Once dumped as CSVs, we converted them to Apache Parquet using AWS Glue.
A guide for that can be found here https://medium.com/@medvedev1088/converting-ethereum-etl-files-to-parquet-399e048ddd30

Once the parquets have been completed, they can be downloaded to a development
machine for analysis.

##### Dogecoin

For Dogecoin, a similar procedure occured as before. We ran a local Dogecoin
node to download and sync the chain to the latest block. We then extract
the transactions, vins, vouts, blocks and coingens into CSV files using
custom code.

The following script ```blockParser/customBitcoinRPC.py``` can be used to
extract the chain into CSV files. Within this, the rpcuser, rpcpasword,
port and url must be changed to be correct.

Once the export is complete, we upload the csv files to Amazon S3,
then parse them into apache spark with amazon glue. The same
guide linked in the Ethereum section can be used, but the python
files used to do the conversion must be replaced with the ones in
```dogechainParsingAWSGlue``` folder.


Once the parquets have been completed, they can be downloaded to a development
machine for analysis.


## Analysis

# Blockchain Parsing

The next stage is to prepare block chain data. For this analysis we
used a mixture of custom tools and public tools.
For our project we downloaded data from full nodes and used the following tools to process them. 

## Blockchains

| Blockchain  | Parsing tool  | 
|---|---|
| Bitcoin  |  BlockSci  | 
| Zcash  | BlockSci  |  
| Dash  |  BlockSci  | 
| Ethereum  | Parsed using AWS Glue from raw data into parquet files  | 
| Ethereum Classic  | Parsed using AWS Glue from raw data into parquet files  | 
| Dogecoin  | Parsed using AWS Glue from raw data into parquet files  | 
| Litecoin  | Parsed using AWS Glue from raw data into parquet files  | 
| Bitcoin Cash  | Parsed using AWS Glue from raw data into parquet files  | 


## BlockSci
### Bitcoin, Zcash, Dash
Blocksci is a block chain analysis and exploration tool.
It can be found on Github https://github.com/citp/BlockSci
For the chains using Blocksci, the user must download the block
chain node files, run a blockchain and sync it to full with
the txindex flag set to 1 (txindex=1).

Then the blockchain files can be parsed to as blocksci format ready for analysis.
Instructions for that can be found in the blocksci documentation.
Details for BlockSci can be found here https://github.com/citp/BlockSci


## AWS Glue into Parquets

As Blocksci does not support all coins, we developed custom tools for
the remaining chains. The block, transaction, vins and vout data must be converted to CSV and then
parquet.
This involves using a tool to extract the rpc data into CSV, then used AWS to parse the raw data into Apache Spark Parquet files. 

### Ethereum and Ethereum Classic
For Ethereum and Ethereum Classic we ran a full node, used Ethereum ETL to extract the data into CSVs, then AWS Glue to parse them into parquets. 

We used this guide https://medium.com/@medvedev1088/exporting-and-analyzing-ethereum-blockchain-f5353414a94e  or 
http://web.archive.org/web/20191002135252/https://medium.com/@medvedev1088/exporting-and-analyzing-ethereum-blockchain-f5353414a94e

The files we used for our process are in the folder. The same file was used for Ethereum and Ethereum Classic, just change the names. 

### Dogecoin, Litecoin, Bitcoin Cash

For these we used the Json RPC to extract the block, transaction, vin and vout data. Copied the data into AWS Glue and parsed them into CSVs. 

You can first config and use the `rpcscript.py` to parse the data from RPC into CSV. 

Then copy the CSV into AWS Glue and run the glue parsing. This will process the CSVs into Parquets.

Finally copy the parquets back to your system. Note, this does not link inputs to previous transactions as we did not need to do this for this project. 