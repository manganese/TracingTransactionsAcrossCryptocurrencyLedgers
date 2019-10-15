# Transactions per day graph

Running the following script will produce a graph showing the number of transactions per day for each of the top 8 currencies. 

This tool requires a csv called `final.csv` which is a csv that is made up of all the transactions. 
e.g. 

```
,timestamp,curIn,curOut,amount
0,1513987126.05,POT,ETH,279.45130072
1,1513987121.7,POT,ETH,279.45130072
2,1513987105.79,ETH,BTC,2.99832
3,1513987105.78,ETH,RDD,0.017
...
```
 # Run 
```
    python txPerDay.py 
``` 