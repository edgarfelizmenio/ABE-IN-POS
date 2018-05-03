import sys
import os
import time
import json
import requests
import datetime
import warnings

import logging

from functools import reduce

from config import *

test_data_dir = 'input'
output_data_dir = 'data'

policy_size = int(sys.argv[1])
num_attributes = int(sys.argv[2])
input_filename = sys.argv[3]

num_txns_str = input_filename.split("_")[0]

users_file_name = 'users_{}_{}_{}.json'.format(policy_size, num_attributes, num_txns_str)
encounter_ids_file_name = '{}_encounter_ids.json'.format(num_txns_str)
transaction_summary_file_name = '{}_{}_{}_query_transaction_summary.txt'.format(policy_size, num_attributes, num_txns_str)

users_file_path = os.path.join(test_data_dir, users_file_name)
input_path = os.path.join(test_data_dir, encounter_ids_file_name)
transaction_summary_path = os.path.join(output_data_dir, transaction_summary_file_name)

with open(users_file_path) as users_file:
    users = json.load(users_file)

with open(input_path) as input_file:
    encounter_ids = json.load(input_file)
    
transaction_times = []
status_codes = []

    def query(encounter_id, user):
        start = time.time()
        response = requests.post('{}/encounters/{}'.format(il_url, encounter_id), headers=headers, auth=auth, json=payload)
        end = time.time()
        print(response.status_code)
        transaction_time = end - start
        transaction_times.append(transaction_time)
        encounters.append(response.json())


def query(encounter_id, user): 
    payload = {
        'private_key': user['private_key']
    }
    start = time.time()
    response = requests.post('{}/encounters/{}'.format(il_upstream_url, encounter_id),
                            headers=headers, 
                            auth=auth,
                            json=payload,
                            verify=False)
    end = time.time()
    print(response.status_code) 
    status_codes.append(response.status_code)
    transaction_time = end - start
    transaction_times.append(transaction_time)

num_encounters = 0
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    eupairs = zip(encounter_ids, users)
    test_start_date = datetime.datetime.utcnow()
    for encounter_id, user in eupairs:
        query(encounter_id, user)
    test_end_date = datetime.datetime.utcnow()

print("number of encounters: {}".format(len(encounter_ids)))

with open(transaction_summary_path, "w") as transaction_summary_file:
    total_time = sum(transaction_times)
    num_transactions = len(transaction_times)
    avg_txn_time = total_time/float(num_transactions)
    rate = 1/avg_txn_time
    success_rate = reduce(lambda a,b: a + b, map(lambda x: 1 if x == 200 else 0, status_codes)) / len(status_codes)
    transaction_summary_file.write('Test start: {}\n'.format(test_start_date))
    transaction_summary_file.write('Test end: {}\n'.format(test_end_date))
    transaction_summary_file.write('Total number of transactions: {}\n'.format(num_transactions))
    transaction_summary_file.write('Total time: {}\n'.format(total_time))
    transaction_summary_file.write('Average transaction time: {}\n'.format(avg_txn_time))
    transaction_summary_file.write('Transactions per second: {}\n'.format(rate))
    transaction_summary_file.write('Success Rate: {}\n'.format(success_rate))
    transaction_summary_file.write('\n')
    transaction_summary_file.writelines(["{}, {}\n".format(status_code, txn_time) for txn_time, status_code in zip(transaction_times, status_codes)])
    