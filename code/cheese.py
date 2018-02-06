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

class Cheese:

    def __init__(self):
        self.cheese_stack = []
        self.trans_list = []
        self.reward = 1

    def blue_cheese(self):
        index = 0
        cheese = {}
        time_stamp = datetime.datetime.now()
        parent_smell = ''
        transactions = []
        nonce = self.proof_of_work(index, time_stamp, transactions, parent_smell)
        smell = self.hash_smell(index, time_stamp, transactions, nonce, parent_smell)
        cheese['index'] = index
        cheese['timestamp'] = str(time_stamp)
        cheese['transactions'] = []
        cheese['previous_smell'] = parent_smell
        cheese['nonce'] = nonce
        cheese['smell'] = smell
        return json.dumps(cheese, ensure_ascii=False)

    def hash_smell(self, index, time_stamp, transactions, nonce, parent_smell):
        return hashlib.sha1(bytes(index) +
                            str(time_stamp).encode('utf-8') +
                            str(transactions).encode('utf-8') +
                            bytes(nonce) +
                            str(parent_smell).encode('utf-8')).hexdigest()

    def proof_of_work(self, index, time_stamp, transactions, parent_smell):
        nonce = 0
        hash_zero = False

        while hash_zero is False:
            nonce += 1
            smell = self.hash_smell(index, time_stamp, transactions, nonce, parent_smell)
            if smell.startswith('0'):
                hash_zero = True
        return nonce

    # When miner receives a transaction, his name and reward will be added into the transaction
    # If they can mine the block, this reward will be his money as part of the transactions collection

    def collect_trans(self, trans_list, trans_details, miner, reward):
        # Convert transaction details into dict and add more information
        trans_details_dict = json.loads(trans_details)
        trans_details_dict['miner'] = miner
        trans_details_dict['reward'] = reward
        # Add the transaction details into current transaction list
        trans_list.append(trans_details_dict)
        return trans_list

    # New transaction details to the others in json format

    def new_trans(self, sender, receiver, amount):
        trans_details = {'from': sender, 'to': receiver, 'amount': amount}
        return json.dumps(trans_details, ensure_ascii=False)


    # transactions: List contains dict obj inside
    # Every time a new transaction is broadcast over the network,
    # member will collect all of them and append into this list
    # and add their identity into this list for reward if they successfully mined it.
    # Mining will be for the whole list with other information


    def cheese_mining(self, cheese_stack, transactions):
        # Convert cheese_stack into dict object
        index = cheese_stack[-1]['index'] + 1
        time_stamp = datetime.datetime.now()
        parent_smell = cheese_stack[-1]['smell']

        # Implement Proof of Work to find a nonce that generate hash starts with 0
        nonce = self.proof_of_work(index,time_stamp,transactions,parent_smell)
        smell = self.hash_smell(index,time_stamp,transactions,nonce,parent_smell)

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

        return json.dumps(cheese, ensure_ascii=False)

    # Update current cheese stack list with whole new cheese stack


    def update_cheese_stack(self, received_cheese_stack, file_name):
        stack_length = len(received_cheese_stack)
        cheese_stack_list = []
        cheese_stack_list = self.load_cheese_stack(file_name)
        local_stack_length = len(cheese_stack_list)
        if stack_length > local_stack_length:
            return False
        else:
            self.store_cheese_stack(received_cheese_stack, file_name)
            return True


    # Add new cheese into cheese_stack
    # cheese_stack can be loaded from local drive


    def add_cheese(self, cheese_stack, cheese):
        # Convert cheese json object into dict object
        cheese_dict = json.loads(cheese)

        # Add cheese into current cheese_stack list
        cheese_stack.append(cheese_dict)
        return cheese_stack


    def store_cheese_stack(self, cheese_stack, file_name):
        with io.open(file_name, 'w', encoding='utf-8') as f:
            f.write(json.dumps(cheese_stack, ensure_ascii=False))


    def load_cheese_stack(self, file_name):
        with open(file_name) as json_data:
            cheese_stack_list = json.load(json_data)
            return cheese_stack_list


    def validate_cheese(self, cheese_stack, cheese):
        # Convert json object into dict object
        cheese_dict = json.loads(cheese)

        # Get the latest cheese details in our last cheese stack list
        index = cheese_stack[-1]['index'] + 1
        smell = cheese_stack[-1]['smell']

        # Get newly received cheese block details to compare index, smell, hash
        new_index = cheese_dict['index']
        new_time_stamp = cheese_dict['timestamp']
        new_transactions = cheese_dict['transactions']
        new_parent_smell = cheese_dict['previous_smell']
        new_nonce = cheese_dict['nonce']
        new_smell = cheese_dict['smell']

        new_hash_smell = self.hash_smell(new_index, new_time_stamp, new_transactions, new_nonce, new_parent_smell)
        print(new_smell)
        print(new_hash_smell)
        if new_index != index:
            return 'Wrong index'
        elif smell != new_parent_smell:
            return 'Wrong parent smell'
        elif new_smell != new_hash_smell:
            return 'Wrong hash'
        else:
            return 'Valid'

newCheese = Cheese()
cheese_stack = []

blue_cheese_dict = json.loads(newCheese.blue_cheese())
cheese_stack.append(blue_cheese_dict)

new_trans = newCheese.new_trans('Member 1', 'Mem 2', 300)
miner1 = 'Miner 1'
reward = 1
trans_list = []
trans_col_list = newCheese.collect_trans(trans_list, new_trans, miner1, reward)
new_mined_json = newCheese.cheese_mining(cheese_stack, trans_col_list)
cheese_stack.append(json.loads(new_mined_json))

new_trans1 = newCheese.new_trans('Member 2', 'Member 3', 150)
miner2 = 'Miner 8'
reward2 = 1
trans_col_list = newCheese.collect_trans(trans_list, new_trans1, miner2, reward2)

new_mined_json1 = newCheese.cheese_mining(cheese_stack, trans_col_list)
cheese_stack.append(json.loads(new_mined_json1))

newCheese.store_cheese_stack(cheese_stack, 'cheese_stack.json')
print(newCheese.load_cheese_stack('cheese_stack.json'))
