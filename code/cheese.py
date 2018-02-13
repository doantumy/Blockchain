import hashlib
import json
import datetime
import io
import time
from ecdsa import VerifyingKey, SigningKey, SECP256k1, BadSignatureError

# Ref: https://medium.com/crypto-currently/lets-build-the-tiniest-blockchain-e70965a248b
# Ref: https://www.dlitz.net/software/pycrypto/doc/#introduction
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



def blue_cheese():

    cheese = {}
    cheese['index'] = 0
    cheese['timestamp'] = str('2018-02-08 21:02:02.760373')
    cheese['transactions'] = []
    cheese['previous_smell'] = ''
    cheese['nonce'], cheese['smell'] = proof_of_work(cheese['index'], cheese['timestamp'], cheese['transactions'], cheese['previous_smell'])
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
    smell = None
    while hash_zero is False:
        nonce += 1
        smell = hash_smell(index, time_stamp, transactions, nonce, parent_smell)
        if smell.startswith('0'):
            hash_zero = True

    return nonce, smell


# When miner receives a transaction, his name and reward will be added into the transaction
# If they can mine the block, this reward will be his money as part of the transactions collection


def collect_trans(trans_list, trans_details, miner, reward=1):
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
    nonce, smell = proof_of_work(index,time_stamp,transactions,parent_smell)

    # Return newly mined cheese block
    cheese = {}
    cheese['index'] = index
    cheese['timestamp'] = str(time_stamp)
    cheese['transactions'] = []
    # i = 0
    # while i <= len(transactions) - 1:
    #     cheese['transactions'].append({'from': transactions[i]['from'], 'to': transactions[i]['to'],
    #                                    'amount': transactions[i]['amount'],
    #                                     'miner': transactions[i]['miner'], 'reward': transactions[i]['reward']})
    #     i +=1

    for trans in transactions:
        cheese['transactions'].append(trans)

    cheese['previous_smell'] = parent_smell
    cheese['nonce'] = nonce
    cheese['smell'] = smell

    return cheese

# Update current cheese stack list with whole new cheese stack


def update_cheese_stack(my_cheese_stack, received_index):
    my_stack_length = my_cheese_stack[-1]["index"]
    if received_index > my_stack_length:
        return True
    else:
        return False


# Add new cheese into cheese_stack when miner sends new mined cheese
# cheese_stack can be loaded from local drive

def add_mined_cheese(my_cheese_stack, cheese, file_path):
    if validate_cheese(my_cheese_stack[-1], cheese):
        my_cheese_stack.append(cheese)
        store_cheese_stack(my_cheese_stack, file_path)
        return True
    else:
        return False

def add_cheeses(my_cheese_stack, cheeses, file_path):
    changed = False
    for ch in cheeses:
        if validate_cheese(my_cheese_stack[-1], ch):
            my_cheese_stack.append(ch)
            changed = True
        else:
            break
    if changed:
        store_cheese_stack(my_cheese_stack, file_path)


def store_cheese_stack(cheese_stack, file_name):
    try:
        with io.open(file_name, 'w', encoding='utf-8') as f:
            f.write(json.dumps(cheese_stack, ensure_ascii=False))
    except IOError:
        print("File %s is not found!" % file_name)
    # raise SystemExit

def load_cheese_stack(file_name):
    try:
        with open(file_name) as json_data:
            cheese_stack_list = json.load(json_data)
            return cheese_stack_list
    except IOError:
        print("File %s is not found!" % file_name)
    # raise SystemExit


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
        print("error1")
        print(smell)
        print(new_parent_smell)
        return False
    elif new_smell != new_hash_smell:
        print("error2")
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
        length -= 1
    return valid


# Auto create trans after 10secs
# Transactions list contains dict objects of random transactions
def auto_trans(delay, transactions_list):
    length = len(transactions_list)
    i = 0
    while i <= length - 1:
        new_tran = new_trans(transactions_list[i]['from'], transactions_list[i]['to'], transactions_list[i]['amount'])
        print(new_tran)
        time.sleep(delay)
        i +=1


# Create public & private key random

def key_generator():
    # Create Private key
    signing_key = SigningKey.generate(curve=SECP256k1)
    private_key_string = signing_key.to_string().hex()
    # Create public key
    verifying_key = signing_key.get_verifying_key()
    public_key_string = verifying_key.to_string().hex()
    return private_key_string, public_key_string


def signing_trans(message, private_key_string):
    private_key = bytes.fromhex(private_key_string)
    signing_key = SigningKey.from_string(private_key, curve=SECP256k1)
    signature = signing_key.sign(message).hex()
    return signature


def verifying_trans(message, signature, public_key_string):
    try:
        public_key = bytes.fromhex(public_key_string)
        verifying_key = VerifyingKey.from_string(public_key, curve=SECP256k1)
        return verifying_key.verify(bytes.fromhex(signature), message)
    except BadSignatureError:
        print('BadSignatureError')
        return False


# Load keys from file if there exists
# If not, new keys will be generated and saved to hard drive

def key_load():
    private_key_file = 'sk.key'
    public_key_file = 'vk.key'
    try:
        private_key = open(private_key_file).read()
        public_key = open(public_key_file).read()
        return private_key, public_key
    except FileNotFoundError:
        keys = key_generator()
        open(private_key_file, "w").write(keys[0])
        open(public_key_file, "w").write(keys[1])
        print('New keys created.')
        return keys
#
# my_blue_cheese = cheese.blue_cheese()
# my_cheeses.stack.append(my_blue_cheese)
#
# new_trans0 = cheese.new_trans('Satoshi team', 'UJM', 300)
# miner1 = 'Anh'
# trans_col_list = cheese.collect_trans(my_cheeses.processed_trans_list, new_trans0, miner1)
# new_mined_json = cheese.cheese_mining(my_cheeses.stack, trans_col_list)
# my_cheeses.stack.append(new_mined_json)
#
# new_trans1 = cheese.new_trans('Satoshi team', 'UJM', 200)
# miner2 = 'Anh'
# trans_col_list = cheese.collect_trans(my_cheeses.processed_trans_list, new_trans1, miner2)
# new_mined_json1 = cheese.cheese_mining(my_cheeses.stack, trans_col_list)
# my_cheeses.stack.append(new_mined_json1)
'''
str_message = 'message'
message = str(str_message).encode('utf-8')
keys = key_load('sk.key','vk.key')
private = keys[0]
public = keys[1]
sig = signing_trans(message, private)
print(private)
print(public)
print(sig)
print(verifying_trans(message, sig, public))
'''