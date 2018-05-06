# USAGE:
# docker exec abeinpos_abe-in-pos_1 python3 key_generation_test.py <policy_size> <num_attributes> <num_txns>_encounters.json
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
encounter_ids_file_name = '{}_encounter_ids_{}_{}.json'.format(num_txns_str, policy_size, num_attributes)
transaction_summary_file_name = '{}_{}_{}_save_transaction_summary.txt'.format(policy_size, num_attributes, num_txns_str)

users_file_path = os.path.join(test_data_dir, users_file_name)
input_path = os.path.join(test_data_dir, input_filename)
encounter_ids_path = os.path.join(test_data_dir, encounter_ids_file_name)

transaction_summary_path = os.path.join(output_data_dir, transaction_summary_file_name)

with open(users_file_path) as users_file:
    users = json.load(users_file)

with open(input_path) as input_file:
    encounters = json.load(input_file)

transaction_times_success = []
transaction_times = []
status_codes = []
encounter_ids = []
error_count = 0

def save(encounter, user, retry=False): 
    start = time.time()
    encounter['policy'] = user['policy']
    encounter['user_id'] = user['user_id']
    response = requests.post('{}/encounters/'.format(il_upstream_url),
                            json=encounter, 
                            headers=headers, 
                            auth=auth,
                            verify=False)
    end = time.time()
    print(response.status_code) 
    transaction_time = end - start

    if response.status_code == 201:
        transaction_times_success.append(transaction_time)
        encounter_ids.append({
            'user': user,
            'encounter_id': response.json()['encounter_id']
        })
    else:
        error_count += 1
    if not retry:
        status_codes.append(response.status_code)        
        transaction_times.append(transaction_time)

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    eupair = list(zip(encounters, users))
    test_start_date = datetime.datetime.utcnow()
    for encounter, user in eupair:
        save(encounter, user)
    while error_count > 0:
        retries = error_count
        error_count = 0
        while retries > 0:
            encounter, user = random.choice(eupair)
            save(encounter, user, True)
            retries -= 1
    test_end_date = datetime.datetime.utcnow()

with open(encounter_ids_path, "w") as encounter_ids_file:
    print("number of encounters: {}".format(len(encounter_ids)))
    json.dump(encounter_ids, encounter_ids_file)

with open(transaction_summary_path, "w") as transaction_summary_file:
    total_time = sum(transaction_times)
    num_transactions = len(transaction_times)
    avg_txn_time = total_time/float(num_transactions)
    rate = 1/avg_txn_time

    total_time_success = sum(transaction_times_success)
    avg_txn_time_success = total_time_success/float(num_transactions)
    rate_success = 1/avg_txn_time_success

    successful_transactions = reduce(lambda a,b: a + b, map(lambda x: 1 if x == 201 else 0, status_codes))
    transaction_summary_file.write('Test start: {}\n'.format(test_start_date))
    transaction_summary_file.write('Test end: {}\n'.format(test_end_date))
    transaction_summary_file.write('Total number of transactions: {}\n'.format(num_transactions))
    transaction_summary_file.write('Total time: {}\n'.format(total_time))
    transaction_summary_file.write('Average transaction time: {}\n'.format(avg_txn_time))
    transaction_summary_file.write('Average transaction time (success): {}\n'.format(avg_txn_time_success))
    transaction_summary_file.write('Transactions per second: {}\n'.format(rate))
    transaction_summary_file.write('Transactions per second (success): {}\n'.format(rate_success))
    transaction_summary_file.write('Successful transactions: {}\n'.format(successful_transactions))
    transaction_summary_file.write('\n')
    transaction_summary_file.writelines(["{}, {}\n".format(status_code, txn_time) for txn_time, status_code in zip(transaction_times, status_codes)])
    transaction_summary_file.write('\n')
    transaction_summary_file.writelines(["{}, {}\n".format(201, txn_time) for txn_time in transaction_times_success])