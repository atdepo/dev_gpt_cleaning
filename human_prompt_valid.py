import os
import json
import re

def set_creator():
    with open('output_validated.json', 'r') as f:
        data = json.load(f)
        questions_block = 32
        curr_block_size = 0
        i = 0
        with open('output_blocks.json', 'w') as output_file:
            output_file.write('[')
            for source in data:
                flag = source.get('ValidationPassedFlag', '')
                if flag == "No" or flag == "Uncertain":
                    conv = source['ChatgptSharing'][0]['Conversations'][0]
                    prompt = conv['Prompt']
                    out = {"id": source['Conversation_ID'], "prompt": prompt}
                    json.dump(out, output_file, indent=4)
                    output_file.write(',\n')
            output_file.write(']')

set_creator()
