import sys
import os
import json
import time
import warnings
import requests
import datetime

import logging

from functools import reduce

from config import *

test_data_dir = 'input'
output_data_dir = 'data'

# python3 key_generation_test.py <policy_size> <num_attributes> <num_txns>
policy_size = int(sys.argv[1])
num_attributes = int(sys.argv[2])
num_txns = int(sys.argv[3])

# input_filename
test_users_file_name = os.path.join(test_data_dir, 'run {} {} {}.json'.format(num_txns, policy_size, num_attributes))

users_file_name = 'users_{}_{}_{}.json'.format(policy_size, num_attributes, num_txns)
transaction_summary_file_name = '{}_{}_key_generation_summary.txt'.format(policy_size, num_attributes)

test_users_path = os.path.join(test_data_dir, test_users_file_name)
user_file_path = os.path.join(test_data_dir, users_file_name)

transaction_summary_path = os.path.join(output_data_dir, transaction_summary_file_name)

with open(test_users_file_name.format(policy_size, num_attributes), 'r') as users_file:
    users_meta = json.load(users_file)

transaction_times = []
status_codes = []
users = []
    
def save_user(user_meta):
    user_object = {
        'first_name': user_meta['attributes'][0],
        'last_name': user_meta['attributes'][1],
        'attributes': user_meta['attributes'][2:]
    }
    start = time.time()
    result = requests.post('{}/user/'.format(il_upstream_url),
                        json=user_object,
                        headers=headers,
                        auth=auth,
                        verify=False)
    end = time.time()
    print(result.status_code)
    status_codes.append(result.status_code)
    transaction_time = end - start
    contents = result.json()
    transaction_times.append(transaction_time)
    users.append({
        'user_id': contents['user_id'],
        'private_key': contents['private_key'],
        'policy': user_meta['policy'],
        'attributes': user_meta['attributes']
    })

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    test_start_date = datetime.datetime.utcnow()
    for user_meta in users_meta:
        save_user(user_meta)
    test_end_date = datetime.datetime.utcnow()

with open(user_file_path, "w") as users_file:
    print("number of users: {}".format(len(users)))
    json.dump(users, users_file)

    with open(users_file_name.format(policy_size, num_attributes), 'w') as users_file:
        print(len(users))
        json.dump(users, users_file)

with open(transaction_summary_path, "w") as transaction_summary_file:
    total_time = sum(transaction_times)
    num_transactions = len(transaction_times)
    avg_txn_time = total_time/float(num_transactions)
    rate = 1/avg_txn_time
    success_rate = reduce(lambda a,b: a + b, map(lambda x: 1 if x == 201 else 0, status_codes)) / len(status_codes)
    transaction_summary_file.write('Test start: {}\n'.format(test_start_date))
    transaction_summary_file.write('Test end: {}\n'.format(test_end_date))
    transaction_summary_file.write('Total number of transactions: {}\n'.format(num_transactions))
    transaction_summary_file.write('Total time: {}\n'.format(total_time))
    transaction_summary_file.write('Average transaction time: {}\n'.format(avg_txn_time))
    transaction_summary_file.write('Transactions per second: {}\n'.format(rate))
    transaction_summary_file.write('Success Rate: {}\n'.format(success_rate/len(status_codes)))
    transaction_summary_file.write('\n')
    transaction_summary_file.writelines(["{}, {}\n".format(status_code, txn_time) for txn_time, status_code in zip(transaction_times, status_codes)])