#### Usage of anonymity tools

##### Zcash

We looked at two interactions between the anonymity feature of Zcash and ShapeShift.
Interaction A: Did users who received money from ShapeShift sent their coins into the pool?
Interaction B: Did users send coins from the pool straight to ShapeShift?

Both of these can be run from the ```anonymityTooolZCash.py``` script which
presents these results.

Interaction A looks at whether Phase 2 transactions, i.e. transactions where the curOut is ZEC,
are sent to the pool. This is done by finding the Phase 2 transactions, identifying the output
that was received by the user, and then checking if it has been spent, if so, did the spent
transaction have zero outputs. If this is true, then the coins went into the pool.

Interaction B looks at whether Phase 1 transactions, i.e. transactions whete the curIn is ZEC,
came from coins from the pool. This looks at whether any phase 1 transactions have an input
count of zero.


##### Dash
As Dash's main anonymity feature is coinjoin transactions, we looked at :
Interaction A: Did users who received money from ShapeShift perform a coinjoin right after?
Interaction B: Were coins sent to ShapeShift obtained from a coinjoin?

Our rules for whether a transaction is a coinjoin are:
    - more than 2 inputs
    - more than 2 outputs
    - all outputs have the same value
    - the output value belongs to the set of possible denominations
        (denominations are fixed in Dash)

Interaction A is done by looking at whether users who received money from a Phase 2 transaction,
where Dash is the curOut, peformed a coinjoin right after. This function uses the results
from phase 2, checks the transaction labelled as the Dash transaction, checks if it has been
spent, and if so, whether the spent transactions output follows the rules for a coinjoin.

Interaction B is found by looking for transactions that had been obtained from a coinjoin.
This looks at Phase 1 transactions, where Dash is a curIn, and if the transaction inputs
were originally from the output of a coinjoin. Thus this will cycle through all inputs,
finding if their spent transaction was a type of coinjoin.

The methods to find these results can be found in ```anonymityToolDash.py```