
# Blockchain P2P Processes

1. New transactions are broadcast to all members, all transactions will be contained in a queue FIFO.
2. Each member collects new transactions into a `Cheese` (max 5 transactions for 1 `Cheese`).
3. Each member works on finding a difficult proof-of-work for its `Cheese`.
4. When a member finds a proof-of-work, it broadcasts the `New_Cheese` to all members.
5. Members accept the `New_Cheese` only if all transactions in it are valid and not already spent.
6. Members express their acceptance of the `Cheese` by working on creating the next `Cheese` in the chain, using the hash of the accepted `Cheese` as the previous hash and deleting processed transactions in the queue. 


## Cheese structure
Each `Cheese` has an `index`, a `time_stamp`, a list of `transactions`, a `nonce`,  a `smell` of previous `Cheese` and its proper `smell` (a hash computed from all listed information by using *SHA1*). E.g
```json
{
  "index": 2,
  "timestamp": "2018-02-1 11:23:10.140996",
  "transactions": [
      {
        "from": "Satoshi team",
        "to": "UJM",
        "amount": 3
      },
      {        
        "from": "Na",
        "to": "Anh",
        "amount": 30
      }
    ],
  "previous_smell": "0023dd3ef6af2e7eb8272245cb8ea91b4ecfc3e60af22d8518ef0bba8b4a6b22",
  "nonce": 36,
  "smell": "001edd3ef6af2e7eb8272245cb8ea91b4ecfc3e60af22d8518ef0bba8b4a6b18"
  
}
```
For `BlueCheese`- the original cheese - it is defined nearly the same with normal cheese except that there is no previous `smell`, `index` is `0` and a predefined `content`.

## Transaction format
Each transaction will be a JSON object detailing the sender of the coin, the receiver of the coin, and the amount of CheeseCoin that is being transferred, e.g
```json
{
  "from": "71238uqirbfh894-random-public-key-a-alkjdflakjfewn204ij",
  "to": "93j4ivnqiopvh43-random-public-key-b-qjrgvnoeirbnferinfo",
  "amount": 3
}
```

## Cheese mining
When new transactions are broadcast in the network, **member**s will collect all of them to put into a single `Cheese`. They will verify the transaction (based on digital signatures, spending histories of the senders to prevent fraud ownership and over-spending). They will then try to solve the proof-of-work problem by finding a `nonce` to generate a hash string (`smell`) that begins with at least two `0`. If miner successfully found it,  he will approve the `Cheese`, add it to the longest chain he has and send this new mined `Cheese` to all over the network.

Newly mined `Cheese` will be confirmed when there is at least 2 more consecutive `Cheese`s added to the chain (in the case of bitcoin the number is 5, here we want to make things less complicated). By doing this, we can make sure that the longest chain is the one that most **member**s are working on, which means it contains the most valid blocks. **Member**s in the network should not accept the new `Cheese` right away but wait for more blocks to be added.

## Synchronization
The following rules are used to keep the network in sync.
- When a member generates a new `Cheese`, he broadcasts it to the network.
- When a member connects to a new peer he queries for the latest `Cheese`.
- When a member encounters a `Cheese` that has an index larger than the current known `Cheese`,  he either adds the `New_Cheese` to his current `Cheese_Stack` or queries for the full `Cheese_Stack`.


## Validation
At any given time we must be able to validate if a `Cheese` or a `Cheese_Stack` are valid in terms of integrity. This is true especially when we receive new `Cheeses` from other members and must decide whether to accept them or not.

The algorithm must check :
 - if the `index` of `New_Cheese` is correct?
 - if the `previous_smell` is correct?
 - compute the hash from data and compare it with the current `smell`.
 

# Sequence Diagrams of P2P network

## Tracker & Member 
![Sequence diagram](./img/Member_Tracker.PNG)


## Member & Member 

### Establish connection
![Sequence diagram](./img/connection.PNG)

### Exchange parts (cheese stack) & Update cheese stack
![Sequence diagram](./img/exchange.PNG)

### Inform the others new mined cheese
![Sequence diagram](./img/newblock.PNG)
#### Ask cheese(s) from other member(s)
![Sequence diagram](./img/askCheese.PNG)
### Member connection and syncs
![Sequence diagram](./img/sync.png)
### Member broadcasting
![Sequence diagram](./img/broadcast.png)
# Message structure
## Interactions between Members and Tracker
| Event | Request Message | Response Message | Description |
|---|---|---|---|
| Establish connection between **Member** and **Tracker** |`REQ_CONNECT`  |`0x01-MESSAGE` |**Member** in the network sends request to connect to the **Tracker**. The **Tracker** returns the message with connection status.|
| Ask for member list from the **Tracker** | `REQ_MEM_LIST` |`0x02-MEM_LIST`|**Member** in the network can ask for member list from the **Tracker**, requested **Tracker** will send back a sub-part of the list (`MEM_LIST`) containing members in the form of text. `MEM_LIST` will be defined in the form as followed: `IP Address:Port`;`IP Address:Port` - semicolon will be used to separate between 2 addresses of member.|
| Update member status | `REQ_ALIVE` | `0x03-ALIVE` or nothing| The **Tracker** might sometimes check for the status of its **Member**. if the **Member** is not alive, it should be deleted from the member list of the **Tracker**|

## Interactions among Members

| Event | Request Message | Response Message | Description |
|---|---|---|---|
| Establish connection to other member(s) |`REQ_CONNECT`  |`0x04-MESSAGE`|Member in the network sends request to connect to other member(s) in the net work. The requested member returns the message with connection status.|
| Exchange parts (cheese stack) among members | `0x05-REQ_CS_LENGTH` and `0x05-REQ_CS`  |`0x05-0x01-CHEESE_STACK_LENGTH` and `0x05-0x02-CHEESE_STACK`|Members in the network may send request to ask for cheese stack from the others. The received list (`DATA`) will be defined as in followed format: `IndexNumber,TimeStamp,TransactionDetails(sender,recipient,amount),ParentSmell,Nonce,Smell`;`IndexNumber,TimeStamp,TransactionDetails(sender,recipient,amount),ParentSmell,Nonce,Smell`- semicolon will be used to separate between 2 blocks. The length of the list depends on the number of cheese blocks that member is storing.|
| Update cheese stack | `REQ_UPDATE_CS` | `UPDATE_CS_YES` or `UPDATE_CS_NO`|This happens after the member sent request to ask for cheese stacks from the others. After checking the received cheese stacks from the others, if any of them doesn't get the longest cheese stack, they will receive request to update their current cheese stack with longest cheese stack (`DATA`). Member may or may not accept to this proposal. `DATA` format is defined as in "Exchange parts (cheese stack) among members"|
| Inform the others new mined cheese | `0x07-NEW_CHEESE` |`0x07-NEW_CHEESE_VALID` or `0x07-NEW_CHEESE_INVALID`| When a member successfully mined a new cheese block, he will broadcast this to the network. Other members will check for the validity of the new block and send back the response to the miner and update their copy of the chain if new block is considered valid. `DATA` is defined as followed: `Sender,Recipient,Amount`|
| Ask cheese(s) from other member(s) | `REQ_CHEESE_DATA` | `0x06-CHEESE`| At anytime member in the network can send request to ask for cheese from the others. If the receiver agrees to the request, he will send a response with acceptance and broadcast the transaction data to the network (`RES_CHEESE_DATA`). If he rejects the request, a rejection message will be sent to the requestor. `DATA` is defined as in "Ask cheese(s) from other member(s)", the sender here is the member who receives the request (is being asked to send cheese), the recipient is the requestor of the request.|
