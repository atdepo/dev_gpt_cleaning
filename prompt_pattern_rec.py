import json
from topic_modeler import process_text, call_chatgpt
from dotenv import load_dotenv


def zero_few_shot_patterns():
    system_prompt = """
    You are an AI language model assistant specialized in classifying user prompts based on their structure.
    A "zero-shot" prompt contains an instruction or question without any examples.
    A "few-shot" prompt includes the instruction and one or more examples of the task.
            
    **Task:**
    Given the user prompt below, perform the following steps:
                    
    1. Classification: Determine whether the prompt is "zero-shot" or "few-shot".
    2. Brief Reasoning: Provide a concise explanation for your classification in no more than 70 words.
                    
    **Output Format:**
                    
    - Classification: [Zero-shot/Few-shot]
    - Reasoning: [Your explanation and reasoning in 70 words or fewer]
    """

    with open('datasets/dataset_prompt_step_1_v2.json', 'w') as output_file:
        output_file.write('[')
        with open('datasets/output_filtered.json', 'r') as f:
            data = json.load(f)
            i = 1
            for source in data:
                if source['TopicSoftwareDevelopmentAndEngineeringFlag']:
                    for block in source['ChatgptSharing']:
                        if block.get('Conversations', None) is not None:
                            for conv in block['Conversations']:
                                prompt = process_text(conv['Prompt'])
                                print(f'Sending {i}')
                                result = call_chatgpt(system_prompt, prompt, 200)
                                print(f"Result: {result}")
                                conv['Prompt_Pattern'] = result
                                i += 1
                    json.dump(source, output_file, indent=4)
                    output_file.write(',\n')
        output_file.write(']')


if __name__ == '__main__':
    load_dotenv()
    zero_few_shot_patterns()
