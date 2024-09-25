import json
import os
import re
from random import choices
import requests
from dotenv import load_dotenv

'''
def json_cleaning(filename, source):
    output = 'dataset.json'

    with open(filename, 'r') as f:
        to_write = list()
        data = json.load(f)['Sources']
        for entry in data:
            entry_to_save = dict()
            entry_conv_obj = entry['ChatgptSharing'][0]

            if len(entry_conv_obj) == 0:
                continue

            entry_to_save['source'] = source
            entry_to_save['conversation_title'] = entry_conv_obj.get('Title', '')
            entry_to_save['openai_shared_link'] = entry_conv_obj.get('URL', '')
            entry_to_save['chatgpt_model_version'] = entry_conv_obj.get('Model', '')
            entry_to_save['number_of_prompt'] = entry_conv_obj.get('NumberOfPrompts', '')
            entry_to_save['token_count_prompts'] = entry_conv_obj.get('TokensOfPrompts', '')
            entry_to_save['token_count_answers'] = entry_conv_obj.get('TokensOfAnswers', '')

            conversations = list()
            for conversation in entry_conv_obj.get('Conversations', list()):
                to_save = dict()
                to_save['prompt'] = conversation.get('Prompt', '')
                to_save['answer'] = conversation.get('Answer', ' ').removeprefix('ChatGPT')
                to_save['code_blocks'] = conversation.get('ListOfCode', list())
                conversations.append(to_save)

            entry_to_save['conversation_content'] = conversations
            to_write.append(entry_to_save)

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
'''

def json_aggregator_service(filename, source):
    output = 'dataset.json'

    to_write = list()
    with open(filename, 'r') as f:

        data = json.load(f)['Sources']
        for entry in data:
            entry_conv_obj = entry['ChatgptSharing'][0]

            if len(entry_conv_obj) == 0 or entry_conv_obj['Status'] >200:
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

    if os.path.exists('dataset.json') :
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
        #except Exception as e:
        #    print(f"An error occurred while reading file {filename}: {e}")

def replace_code_blocks(data):
    answer = data["Answer"]
    for block in data["ListOfCode"]:
        answer = answer.replace(block["ReplaceString"], block["Content"])
    return answer

def create_input(content):
    input = {
        "model": "lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
        "messages": [
            {"role": "system",
             "content": "Analyze the following conversation and determine if it is related to software development, code generation, bug fixing, or other technical programming contexts. Please respond with 'Yes' if it is related to these contexts, and 'No' if it is not. Provide no additional information or explanation beyond a 'Yes' or 'No'."},
            {"role": "user", "content": content}
        ],
        "temperature": 0.7,
        "max_tokens": -1,
        "stream": False
    }

    return input

def send_input(mod_input):
    api_url = os.getenv('API_URL')
    headers = {
        'Content-Type': 'application/json'
    }

    # Sending a POST request with JSON data
    response = requests.post(api_url, json=mod_input, headers=headers)

    # Check if the response contains valid JSON
    if response.status_code == 200:
        try:
            # Convert response to JSON
            response_json = response.json()
            return response_json['choices'][0]['message']['content']

        except json.JSONDecodeError:
            print("Failed to decode JSON from response")
            return None
    else:
        print(f"Request failed with status code: {response.status_code}. {mod_input}")
        return None

def topic_modeling():

    with open('dataset.json', 'r') as f:
        data = json.load(f)
        i = 0
        for source in data:
            for entry in source:
                full_conversation = ""
                for conv in entry['ChatgptSharing'][0]['Conversations']:

                    #ans = replace_code_blocks(conv)
                    #ans = ans.replace('"', ' ')
                    #ans = re.sub(r'\\.', '', ans)
                    prp = conv['Prompt'].replace('"',' ')
                    prp = re.sub(r'\\.', '', prp)
                    full_conversation += f"User: {prp}\n"

                model_input = create_input(full_conversation)
                print(f"Sending input {i}")
                result = send_input(model_input)
                if result is not None:
                    entry['TopicSoftwareDevelopmentFlag'] = True if result == "Yes" else False
                    print(f"Received Answer for input {i}: {result}")
                    #print(entry)
                i+=1
    with open('dataset.json', 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == '__main__':
    load_dotenv()
    #json_aggregator()
    topic_modeling()


