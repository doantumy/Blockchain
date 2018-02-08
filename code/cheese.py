import hashlib
import json
import datetime
import io

# Ref: https://medium.com/crypto-currently/lets-build-the-tiniest-blockchain-e70965a248b
'''
Author: DOAN Tu-My
Def Lists:

1. blue_cheese()
2. hash_smell(index,time_stamp,transactions,nonce,parent_smell)
3. proof_of_work(index,time_stamp,transactions,parent_smell)
4. collect_trans(trans_list, trans_details, miner, reward)
5. new_trans(sender, receiver, amount)
6. cheese_mining(cheese_stack, transactions)
7. update_cheese_stack(cheese_stack, file_name) - need to test
8. add_cheese(cheese_stack, cheese)
9. store_cheese_stack(cheese_stack, file_name)
10.load_cheese_stack(file_name)
11.validate_cheese(cheese_stack, cheese)
12.

'''
my_cheese_stack = []
trans_list = []
reward = 1


def blue_cheese():
    index = 0
    cheese = {}
    time_stamp = '2018-02-08 21:02:02.760373'
    parent_smell = ''
    transactions = []
    nonce = proof_of_work(index, time_stamp, transactions, parent_smell)
    smell = hash_smell(index, time_stamp, transactions, nonce, parent_smell)
    cheese['index'] = index
    cheese['timestamp'] = str(time_stamp)
    cheese['transactions'] = []
    cheese['previous_smell'] = parent_smell
    cheese['nonce'] = nonce
    cheese['smell'] = smell
    return cheese


def hash_smell(index, time_stamp, transactions, nonce, parent_smell):
    return hashlib.sha1(bytes(index) +
                        str(time_stamp).encode('utf-8') +
                        str(transactions).encode('utf-8') +
                        bytes(nonce) +
                        str(parent_smell).encode('utf-8')).hexdigest()


def proof_of_work(index, time_stamp, transactions, parent_smell):
    nonce = 0
    hash_zero = False

    while hash_zero is False:
        nonce += 1
        smell = hash_smell(index, time_stamp, transactions, nonce, parent_smell)
        if smell.startswith('0'):
            hash_zero = True
    return nonce


# When miner receives a transaction, his name and reward will be added into the transaction
# If they can mine the block, this reward will be his money as part of the transactions collection


def collect_trans(trans_list, trans_details, miner, reward):
    trans_details['miner'] = miner
    trans_details['reward'] = reward
    # Add the transaction details into current transaction list
    trans_list.append(trans_details)
    return trans_list


# New transaction details to the others in json format


def new_trans(sender, receiver, amount):
    trans_details = {'from': sender, 'to': receiver, 'amount': amount}
    return trans_details


# transactions: List contains dict obj inside
# Every time a new transaction is broadcast over the network,
# member will collect all of them and append into this list
# and add their identity into this list for reward if they successfully mined it.
# Mining will be for the whole list with other information


def cheese_mining(cheese_stack, transactions):
    # Convert cheese_stack into dict object
    index = cheese_stack[-1]['index'] + 1
    time_stamp = datetime.datetime.now()
    parent_smell = cheese_stack[-1]['smell']

    # Implement Proof of Work to find a nonce that generate hash starts with 0
    nonce = proof_of_work(index,time_stamp,transactions,parent_smell)
    smell = hash_smell(index,time_stamp,transactions,nonce,parent_smell)

    # Return newly mined cheese block
    cheese = {}
    cheese['index'] = index
    cheese['timestamp'] = str(time_stamp)
    cheese['transactions'] = []
    i = 0
    while i <= len(transactions) - 1:
        cheese['transactions'].append({'from': transactions[i]['from'], 'to': transactions[i]['to'],
                                       'amount': transactions[i]['amount'],
                                        'miner': transactions[i]['miner'], 'reward': transactions[i]['reward']})
        i +=1

    cheese['previous_smell'] = parent_smell
    cheese['nonce'] = nonce
    cheese['smell'] = smell

    return cheese

# Update current cheese stack list with whole new cheese stack


def update_cheese_stack(received_cheese_stack, file_name):
    stack_length = len(received_cheese_stack)
    cheese_stack_list = load_cheese_stack(file_name)
    local_stack_length = len(cheese_stack_list)
    if stack_length > local_stack_length:
        return False
    else:
        store_cheese_stack(received_cheese_stack, file_name)
        return True


# Add new cheese into cheese_stack when miner sends new mined cheese
# cheese_stack can be loaded from local drive


def add_mined_cheese(local_cheese_stack, cheese, file_name):
    # Check received latest index with our index
    local_stack_list = load_cheese_stack(file_name)
    valid = validate_cheese(local_stack_list[-1], cheese)
    if valid:
        # Add new cheese into local stack
        local_stack_list.append(cheese)
        # Save local file
        store_cheese_stack(local_stack_list, file_name)
        return True
    else:
        return False


def store_cheese_stack(cheese_stack, file_name):
    try:
        with io.open(file_name, 'w', encoding='utf-8') as f:
            f.write(json.dumps(cheese_stack, ensure_ascii=False))
    except IOError:
        print("Image file %s is not found!" % file_name)
    raise SystemExit


def load_cheese_stack(file_name):
    try:
        with open(file_name) as json_data:
            cheese_stack_list = json.load(json_data)
            return cheese_stack_list
    except IOError:
        print("Image file %s is not found!" % file_name)
    raise SystemExit


def validate_cheese(previous_cheese, next_cheese):
    # Get the latest cheese details in our last cheese stack list
    index = previous_cheese['index'] + 1
    smell = previous_cheese['smell']

    # Get newly received cheese block details to compare index, smell, hash
    new_index = next_cheese['index']
    new_time_stamp = next_cheese['timestamp']
    new_transactions = next_cheese['transactions']
    new_parent_smell = next_cheese['previous_smell']
    new_nonce = next_cheese['nonce']
    new_smell = next_cheese['smell']
    new_hash_smell = hash_smell(new_index, new_time_stamp, new_transactions, new_nonce, new_parent_smell)

    if new_index != index:
        print(index)
        print(new_index)
        return False
    elif smell != new_parent_smell:
        print(smell)
        print(new_parent_smell)
        return False
    elif new_smell != new_hash_smell:
        print(new_smell)
        print(new_hash_smell)
        return False
    else:
        return True


def validate_cheese_stack(received_cheese_stack_list):
    i = 0
    length = len(received_cheese_stack_list)
    valid = True
    # Checking first cheese & second one and so on...
    while i <= length - 1 and valid == True:
        valid = validate_cheese(received_cheese_stack_list[i], received_cheese_stack_list[i+1])
        length -=1
    return valid

blue_cheese_dict = blue_cheese()
my_cheese_stack.append(blue_cheese_dict)

new_trans0 = new_trans('Member 1', 'Mem 2', 300)
miner1 = 'Miner 1'
reward = 1
trans_list = []
trans_col_list = collect_trans(trans_list, new_trans0, miner1, reward)
new_mined_json = cheese_mining(my_cheese_stack, trans_col_list)
my_cheese_stack.append(new_mined_json)

new_trans1 = new_trans('Member 2', 'Member 3', 150)
miner2 = 'Miner 8'
reward2 = 1
trans_col_list = collect_trans(trans_list, new_trans1, miner2, reward2)

new_mined_json1 = cheese_mining(my_cheese_stack, trans_col_list)
my_cheese_stack.append(new_mined_json1)

store_cheese_stack(my_cheese_stack, 'cheese_stack.json')
print(load_cheese_stack('cheese_stack.json'))
