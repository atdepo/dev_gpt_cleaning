import json
import os
import re
import requests


def json_aggregator_service(filename, source):
    output = 'dataset.json'

    to_write = list()
    with open(filename, 'r') as f:

        data = json.load(f)['Sources']
        for entry in data:
            entry_conv_obj = entry['ChatgptSharing'][0]

            if len(entry_conv_obj) == 0 or entry_conv_obj['Status'] > 200:
                continue
            entry_conv_obj['Source'] = source
            if entry_conv_obj['HTMLContent'] is not None:
                entry_conv_obj.pop('HTMLContent')
            to_write.append(entry)

    content = []
    if os.path.exists(output):
        with open(output, 'r') as f:
            try:
                content = json.load(f)
            except json.JSONDecodeError:
                content = []

    # Append new data
    content.append(to_write)

    # Write updated data back to the file
    with open(output, 'w') as f2:
        json.dump(content, f2, indent=2)


def json_aggregator():
    if os.path.exists('dataset.json'):
        print("removing the old dataset")
        os.remove('dataset.json')

    directory = 'last_snapshot'

    for filename in os.listdir(directory):
        if not filename.endswith('.json'):
            continue

        try:
            source = filename[0] + filename.split('_')[1][0]
            json_aggregator_service(f"{directory}/{filename}", source)
            print(f"Successfully read {filename}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from file {filename}: {e}")
        # except Exception as e:
        #    print(f"An error occurred while reading file {filename}: {e}")


def replace_code_blocks(data):
    answer = data["Answer"]
    for block in data["ListOfCode"]:
        answer = answer.replace(block["ReplaceString"], block["Content"])
    return answer