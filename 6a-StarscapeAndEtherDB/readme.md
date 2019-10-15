# Case studies: Starscape and EtherScamDB

This section explains and walks you through how we investigated these two case studies. 

## StarScape

As explained in the paper, we identified that some of the funds from Starscape Capital went through ShapeShift. This details the process of how we discovered this. By searching online we found the address that belonged to Starscape was ETH address: 0xBA9e83D6eF2fb1c189a087C1Ea86065AE0143e10

We then obtained all the transaction hashes that this address has sent to and the addresses that received their funds. This can be done by going to EtherScan.io and filtering by outgoing txs. 
https://etherscan.io/txs?a=0xba9e83d6ef2fb1c189a087c1ea86065ae0143e10&f=2

All of these addresses where then fed into the ShapeShift `txstat` API which told us whether or not it was an address belonging to ShapeShift. 

From this we found the following. 

Starscape address did 109 shapeshifts in total, 6 to ETH, 103 to XMR
For the XMR transactions it was a total of 1388.3986095799996,
Range of the transactions values were from

    XMR 2.96928859 to 14.16857521
    or
    ETH 1.0 to  4.7
    (1.0: 1, 1.6: 1, 3.61803925: 1, 4.0: 3, 4.5: 18, 4.6: 49, 4.7: 30})

These were deposited into the following XMR addresses
    
    33 transactions
    387.65073458000006 XMR
    45QqEVUrUzKGpbSa2oGPBXWG8BvvGrKTH5ZAEVjd3UDgBFF1vsZW5LBfdn3Jg77ENqa9TcFoJnyZdfrmqjEKYP5Z44o3Xuf
    View key: 410dbf5b2e77f0e6fa62584cbb72b6c62a8128be55b61ce85157824256edb81b
    Spend key: 63f7d38d94a3e05e95c8238b6e1312aef04aaaf956c7741b3ab9401d50ccfb3d
    
    75 transactions
    486P4wtcCwp5DFJGVtVb2JKAXyBPWSY7ob28W3ZcfyuTNBjZcZeUr7zSpAVfksL41U62PMhdf9Tt94SZkzKa5p3x5ocM5aa
    997.7785864099999 XMR
    View key: a84086718ecbc19a53abfb1e71edff1e092e1a8eae3d5e14922f4c8f6084f72a
    Spend key: aabd063a511b1f192d42dce13e19636c9904545a41b7decb639def68ecb0e27e
    
    1 transaction
    2.96928859 XMR
    49tojKF51gxBySBndsMeHjTaT3xFgyS1NYHaQXZaQDeLPsd9J8D169yjeGHWct4VEtPGaSvaqyiEKaqyq9isgJqbNLubtQd 
    View key: bf63a644f3461cfef154aec6c426dd8522921015e7c3e8ca57c9e2e859d03ebd
    Spend key: da3fb56480e64d419a723a1076fffe9ee44ab120f59649bb0ba7f573f52ccd88

The associated code for parsing this can be found in`starscape.py`

## EtherScamDB

EtherScamDB10 is a website that, based on user reports that are manually investigated by its operators, collects and lists Ethereum addresses that have been involved in scams. 

We downloaded all the scams, their addresses and looked to see if the scammers used Shapeshift after to move their funds. The process of this is very similar to above. 

This requires an API key from EtherScan.io for using their Transaction API, please replace the variable in the script. 

You may then run the script `etherscamdb.py`