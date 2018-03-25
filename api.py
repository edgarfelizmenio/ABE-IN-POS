import os
from flask import jsonify, send_from_directory

from app import app

import models

# output_filename = 'key_generation-{}-{}-{}-{}-{}'.format(num_threads, num_users, file_size, policy_size, num_attributes)
@app.route('/test/keygen/<int:num_threads>/<int:num_users>/<int:file_size>/<int:policy_size>/<int:num_attributes>')
def test_keygen(num_threads, num_users, file_size, policy_size, num_attributes):
    file_name = models.keygen_file_name.format(num_threads, num_users, file_size, policy_size, num_attributes)
    if os.path.exists(os.path.join(models.results_dir, file_name)):
        return send_from_directory(models.results_dir, file_name)
    else:
        models.key_generation_test.delay(num_threads, num_users, file_size, policy_size, num_attributes)
        response = {'status': 200, 'message': 'Key generation test started.'}
        pos_response = jsonify(response)
        return pos_response        

@app.route('/test/save/<int:num_threads>/<int:num_users>/<int:file_size>/<int:policy_size>/<int:num_attributes>')
def test_save(num_threads, num_users, file_size, policy_size, num_attributes):
    file_name = models.save_file_name.format(num_threads, num_users, file_size, policy_size, num_attributes)
    if os.path.exists(os.path.join(models.results_dir, file_name)):
        return send_from_directory(models.results_dir, file_name)
    else:
        models.save_encounter_test.delay(num_threads, num_users, file_size, policy_size, num_attributes)
        response = {'status': 200, 'message': 'Save test started.'}
        pos_response = jsonify(response)
        return pos_response

@app.route('/test/query/<int:num_threads>/<int:num_users>/<int:file_size>/<int:policy_size>/<int:num_attributes>')
def test_query(num_threads, num_users, file_size, policy_size, num_attributes):
    file_name = models.query_file_name.format(num_users, file_size)
    if os.path.exists(os.path.join(models.results_dir, file_name)):
        return send_from_directory(models.results_dir, file_name)
    else:
        models.query_encounter_test.delay(num_threads, num_users, file_size, policy_size, num_attributes)
        response = {'status': 200, 'message': 'Query test started.'}
        pos_response = jsonify(response)
        return pos_response