import json
import os
import re
import requests


# Function to aggregate JSON data from a given file and write it to 'dataset.json'
def json_aggregator_service(filename, source):
    output = 'dataset.json'

    to_write = list()
    # Open the specified input JSON file
    with open(filename, 'r') as f:
        data = json.load(f)['Sources']

        # Iterate over each entry in the data
        for entry in data:
            entry_conv_obj = entry['ChatgptSharing'][0]

            # Skip if conversation object is empty or if its status is greater than 200
            if len(entry_conv_obj) == 0 or entry_conv_obj['Status'] > 200:
                continue

            # Add the source attribute to the entry
            entry_conv_obj['Source'] = source

            # Remove the 'HTMLContent' key from the entry if it exists
            if entry_conv_obj['HTMLContent'] is not None:
                entry_conv_obj.pop('HTMLContent')

            # Add the updated entry to the list to be written
            to_write.append(entry)

    # Load existing content from 'dataset.json' if it exists
    content = []
    if os.path.exists(output):
        with open(output, 'r') as f:
            try:
                content = json.load(f)
            except json.JSONDecodeError:
                # Handle case where the existing JSON file is invalid or empty
                content = []

    # Append new data to the existing content
    content.append(to_write)

    # Write the updated content back to 'dataset.json'
    with open(output, 'w') as f2:
        json.dump(content, f2, indent=2)


# Function to remove the old dataset file and aggregate new data from the 'last_snapshot' directory
def json_aggregator():
    # Check if 'dataset.json' exists, remove it to create a new one
    if os.path.exists('dataset.json'):
        print("Removing the old dataset")
        os.remove('dataset.json')

    directory = 'last_snapshot'

    # Iterate over all files in the specified directory
    for filename in os.listdir(directory):
        if not filename.endswith('.json'):
            # Skip non-JSON files
            continue

        try:
            # Extract source information from the filename
            source = filename[0] + filename.split('_')[1][0]

            # Call the aggregator service to process the file
            json_aggregator_service(f"{directory}/{filename}", source)
            print(f"Successfully read {filename}")

        # Handle any JSON decoding errors
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from file {filename}: {e}")
        # Uncomment the block below to handle other generic exceptions
        # except Exception as e:
        #    print(f"An error occurred while reading file {filename}: {e}")


# Function to replace code blocks in an answer with the actual code from a list of code blocks
def replace_code_blocks(data):
    answer = data["Answer"]

    # Replace each placeholder in the answer with its corresponding code content
    for block in data["ListOfCode"]:
        answer = answer.replace(block["ReplaceString"], block["Content"])

    return answer
