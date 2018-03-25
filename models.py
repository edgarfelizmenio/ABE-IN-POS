import os
import time
import json
import datetime
import requests
import concurrent.futures

from requests.auth import HTTPBasicAuth
from multiprocessing.pool import ThreadPool

from config import *
import traceback

from app import celery

test_data_dir = 'test_data'
test_users_file_name = os.path.join(test_data_dir, 'users_{}_{}.json')
test_encounters_file_name = os.path.join(test_data_dir, 'encounters_{}kb.json')

results_dir = 'results'

users_file_name = 'users_{}_{}.json'
encounter_ids_file_name = 'encounter_ids.json'
encounters_file_name = 'encounters.json'

keygen_file_name = os.path.join(results_dir, 'time_key_generation_{}_{}_{}_{}_{}.txt')
save_file_name = os.path.join(results_dir, 'time_save_encounter_{}_{}_{}_{}_{}.txt')
query_file_name = os.path.join(results_dir, 'time_query_encounter_{}_{}_{}_{}_{}.txt')

if not os.path.exists(results_dir):
    os.mkdir(results_dir)

@celery.task()
def key_generation_test(num_threads, num_users, file_size, policy_size, num_attributes):
    with open(test_users_file_name.format(policy_size, num_attributes), 'r') as users_file:
        users_meta = json.load(users_file)

    transaction_times = []
    users = []
    
    def save_user(user_meta):
        user_object = {
            'first_name': user_meta['attributes'][0],
            'last_name': user_meta['attributes'][1],
            'attributes': user_meta['attributes'][2:]
        }
        start = time.time()
        result = requests.post('{}/user'.format(il_url),
                            json=user_object,
                            headers=headers,
                            auth=auth)
        end = time.time()
        print(result.status_code)
        transaction_time = end - start
        contents = result.json()
        transaction_times.append(transaction_time)
        users.append({
            'user_id': contents['user_id'],
            'private_key': contents['private_key'],
            'policy': user_meta['policy'],
            'attributes': user_meta['attributes']
        })

    pool = ThreadPool(num_users)

    test_start_date = datetime.datetime.utcnow()

    for user_meta in users_meta:
        pool.apply(save_user, (user_meta,))

    pool.close()
    pool.join()
    test_end_date = datetime.datetime.utcnow()

    with open(users_file_name.format(policy_size, num_attributes), 'w') as users_file:
        print(len(users))
        json.dump(users, users_file)

    with open(keygen_file_name.format(num_threads, num_users, file_size, policy_size, num_attributes), 'w') as transaction_times_file:
        total_time = sum(transaction_times)
        num_transactions = len(transaction_times)
        avg_txn_time = total_time/float(num_transactions)
        rate = 1/avg_txn_time
        transaction_times_file.write('Key Generation Test - {} Thread, {} User, {} kb, {} attributes in policy, {} attributes in key\n'.format(
            num_threads, num_users, file_size, policy_size, num_attributes
        ))
        transaction_times_file.write('Test start: {}\n'.format(test_start_date))
        transaction_times_file.write('Test end: {}\n'.format(test_end_date))
        transaction_times_file.write('Total number of transactions: {}\n'.format(num_transactions))
        transaction_times_file.write('Total time: {}\n'.format(total_time))
        transaction_times_file.write('Average transaction time: {}\n'.format(avg_txn_time))
        transaction_times_file.write('Transactions per second: {}\n'.format(rate))
        transaction_times_file.write('\n')
        transaction_times_file.writelines(["{}\n".format(txn_time) for txn_time in transaction_times])        

@celery.task()
def save_encounter_test(num_threads, num_users, file_size, policy_size, num_attributes):
    with open(test_encounters_file_name.format(file_size), 'r') as encounters_file:
        encounters = json.load(encounters_file)
    with open(users_file_name.format(policy_size, num_attributes), 'r') as users_file:
        users = json.load(users_file)

    pool = ThreadPool(num_users)

    transaction_times = []
    encounter_ids = []

    def save(encounter, user):
        encounter['policy'] = user['policy']
        encounter['user_id'] = user['user_id']
        start = time.time()
        response = requests.post('{}/encounters/'.format(il_url), json=encounter, headers=headers, auth=auth)
        end = time.time()
        print(response.status_code)
        transaction_time = end - start
        transaction_times.append(transaction_time)
        encounter_ids.append(response.json()['encounter_id'])

    pool = ThreadPool(num_users)

    test_start_date = datetime.datetime.utcnow()
    for encounter, user in zip(encounters, users):
        pool.apply(save, (encounter, user))

    pool.close()
    pool.join()
    test_end_date = datetime.datetime.utcnow()

    with open(encounter_ids_file_name, 'w') as encounter_ids_file:
        print(len(encounter_ids))
        json.dump(encounter_ids, encounter_ids_file)

    with open(save_file_name.format(num_threads, num_users, file_size, policy_size, num_attributes), 'w') as transaction_times_file:
        total_time = sum(transaction_times)
        num_transactions = len(transaction_times)
        avg_txn_time = total_time/float(num_transactions)
        rate = 1/avg_txn_time
        transaction_times_file.write('Save Encounter Test - {} Thread, {} User, {} kb, {} attributes in policy, {} attributes in key\n'.format(
            num_threads, num_users, file_size, policy_size, num_attributes
        ))
        transaction_times_file.write('Test start: {}\n'.format(test_start_date))
        transaction_times_file.write('Test end: {}\n'.format(test_end_date))
        transaction_times_file.write('Total number of transactions: {}\n'.format(num_transactions))
        transaction_times_file.write('Total time: {}\n'.format(total_time))
        transaction_times_file.write('Average transaction time: {}\n'.format(avg_txn_time))
        transaction_times_file.write('Transactions per second: {}\n'.format(rate))
        transaction_times_file.write('\n')
        transaction_times_file.writelines(["{}\n".format(txn_time) for txn_time in transaction_times])

@celery.task()
def query_encounter_test(num_threads, num_users, file_size, policy_size, num_attributes):
    with open(encounter_ids_file_name, 'r') as encounter_ids_file:
        encounter_ids = json.load(encounter_ids_file)
    with open(users_file_name.format(policy_size, num_attributes), 'r') as users_file:
        users = json.load(users_file)

    transaction_times = []
    encounters = []

    def query(encounter_id, user):
        payload = {
            'private_key': user['private_key']
        }
        start = time.time()
        response = requests.post('{}/encounters/{}'.format(il_url, encounter_id), headers=headers, auth=auth, json=payload)
        end = time.time()
        print(response.status_code)
        transaction_time = end - start
        transaction_times.append(transaction_time)
        encounters.append(response.json())

    pool = ThreadPool(num_users)
    test_start_date = datetime.datetime.utcnow()
    for encounter_id, user in zip(encounter_ids, users):
        pool.apply(query, (encounter_id, user))

    pool.close()
    pool.join()
    test_end_date = datetime.datetime.utcnow()

    with open(encounters_file_name, 'w') as encounters_file:
        print(len(encounters))
        json.dump(encounters, encounters_file)

    with open(query_file_name.format(num_threads, num_users, file_size, policy_size, num_attributes), 'w') as transaction_times_file:
        total_time = sum(transaction_times)
        num_transactions = len(transaction_times)
        avg_txn_time = total_time/float(num_transactions)
        rate = 1/avg_txn_time
        transaction_times_file.write('Query Encounter Test - {} Thread, {} User, {} kb, {} attributes in policy, {} attributes in key\n'.format(
            num_threads, num_users, file_size, policy_size, num_attributes
        ))
        transaction_times_file.write('Test start: {}\n'.format(test_start_date))
        transaction_times_file.write('Test end: {}\n'.format(test_end_date))
        transaction_times_file.write('Total number of transactions: {}\n'.format(num_transactions))
        transaction_times_file.write('Total time: {}\n'.format(total_time))
        transaction_times_file.write('Average transaction time: {}\n'.format(avg_txn_time))
        transaction_times_file.write('Transactions per second: {}\n'.format(rate))
        transaction_times_file.write('\n')
        transaction_times_file.writelines(["{}\n".format(txn_time) for txn_time in transaction_times])


