import os
import json
import base64

source_dir_name = 'test_data'
images_dir_name = os.path.join(source_dir_name, 'images')

source_file_name = os.path.join(source_dir_name, 'sample.json')

with open(source_file_name, 'r') as source_file:
    encounters = json.load(source_file)

with open(os.path.join(source_dir_name, 'encounters_8kb.json'), 'w') as default_input_file:
    json.dump(encounters, default_input_file)

image_file_names = os.listdir(images_dir_name)
for image_file_name in image_file_names:
    with open(os.path.join(images_dir_name, image_file_name), 'rb') as image_file:
        image_bytes = base64.b64encode(image_file.read())

    image_string = str(image_bytes, 'utf-8')
    for encounter in encounters:
        encounter['image'] = image_string

    with open(os.path.join(source_dir_name, 'encounters_{}.json'.format(image_file_name[:-4])), 'w') as output_file_name:
        json.dump(encounters, output_file_name)