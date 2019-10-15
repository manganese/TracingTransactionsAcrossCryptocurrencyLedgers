# Tracing Transactions Across Cryptocurrency Ledgers

This is the source code used in the research paper:

    Tracing Transactions Across Cryptocurrency Ledgers
    Haaroon Yousaf, George Kappos, Sarah Meiklejohn
    Usenix Security 2019
    https://arxiv.org/abs/1810.12786

All authors are supported by the EUH2020 TITANIUM project under grant agreement number 740558.

[![DOI](https://zenodo.org/badge/215335122.svg)](https://zenodo.org/badge/latestdoi/215335122)
    
Please read this ```readme.md``` from start to finish before attempting
any of this analysis.

## Prerequisites

* Storage space to process upto 8 block chains worth of data (or space
required for the block chains being analysed)
* Access to powerful machines or Amazon EC2
* Clone this repository
* Python 3.6
* Install requirements.txt
* BlockSci https://github.com/citp/BlockSci

As this analysis looks at tracing transactions across ledgers, primarily
focusing on data obtained from the ShapeShift API, it is necessary for
user to have such data, or data in the same format, before proceeding

# Guide

Each section has its own folder. Each folder has its own instructions in a readme.md file. 

* ShapeShift Data Collection, 1-Scraper
* Short data example,  2-TxPerdayGraph
* Parsing Blockchain Data,  3-BlockchainParsing
* Identifying Blockchain Transactions and passthrough, 4-IdentifyingTransactions
* Clustering heuristics, 5-ClusteringHeuristics
* Case study, StarScape and EtherscamDB, 6a-StarscapeAndEtherDB
* Anonymity Tools, 6b-AnonymityTools











