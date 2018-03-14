## Difficulties & Improvement
 Despite the succes we get, we still have a lots of problem to solve.
- In our protocol, we accept to add a new mined block right away to the blockchain, then broadcast it to all other miners.
Therefore, there is a  conflict when many miners success to mine a new block simultaneously.
To solve this kind of problem, we suggest to increase the difficulty of mining or change the strategy of mining and verification.
- To create a valid transaction, we used private key of sender to encode the transaction's content 
to a signature. To check its validation, we just need to unblock the signature by the sender's public key. 
However, we also can combine private key of sender and public key of receiver to encode the message, that will make the transaction more security.
