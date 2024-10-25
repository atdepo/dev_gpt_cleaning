import json
from topic_modeler import process_text, call_chatgpt
from dotenv import load_dotenv


def classification_step():
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

    with open('zero-few-iterations/dataset_prompt_step_1_v1.json', 'w') as output_file:
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

def feedback_step():
    system_prompt = """
        **Role**: You are an expert linguist and text classifier with extensive experience in nuanced text analysis.
        **Task**: Please review the following text and the previous classification along with its reasoning. Your goal is to evaluate the accuracy and completeness of the classification.
        **Instructions**:

        1. Evaluation:
           - Think step by step about the key points of zero shot and few shot prompting, their main characteristics and composition.
           - Determine whether the classification accurately reflects the content of the text, also using the previous reasoning to further understand how such classification was produced.
           - Assess the correctness provided for the classification. Read again your answer if you are not sure, be critical.
           - Do not infer nothing that is not written in the prompt, focus solely on the content.
        
        2. Feedback:
           - If you agree with the classification or you think that the classification is accurate, and have no feedbacks or suggestion output "None". If your only feedbacks relies on strengthening the reasoning or the fact that the reasoning could have included more detail, also output "None"
           - If you disagree or see areas for improvement, identify the errors, misclassifications, and overlooked aspects. Give as an output feedbacks on the reasoning produced and suggestions on areas to explore further to refine the classification. For example, if you notice that the previous classification has classified a prompt as "few-shots" but the llm took the code provided as an example but was only given to perform some operations on it, make it clear in the feedback and suggestion part. 
        
        **Response Format if you disagree**:
            Feedback:
            - [Feedback point 1 (at most 70 words)]
            - [Feedback point 2 (at most 70 words)]
            Suggestions:
            - [Suggestion 1 (at most 70 words)]
            - [Suggestion 2 (at most 70 words)]
        
        **Response Format if you agree**:
            None
        """

    with open('zero-few-iterations/dataset_prompt_step_2_v5.json', 'w') as output_file:
        output_file.write('[')
        with open('zero-few-iterations/dataset_prompt_step_3_v4.json', 'r') as f:
            data = json.load(f)
            i = 1
            for source in data:
                if source['TopicSoftwareDevelopmentAndEngineeringFlag']:
                    for block in source['ChatgptSharing']:
                        if block.get('Conversations', None) is not None:
                            for conv in block['Conversations']:
                                feedback = conv.get('Feedbacks', 'None')
                                if feedback != 'None':
                                    prompt = process_text(conv['Prompt'])
                                    res = conv['Prompt_Pattern']
                                    classification, reasoning = res.split('\n')
                                    to_send = f"""
                                    [CLASSIFICATION_START]{classification}[CLASSIFICATION_END]
                                    [REASONING_START]{reasoning}[REASONING_END]
                                    [PROMPT_ANALYZED_START]{prompt}[PROMPT_ANALYZED_END]
                                    """
                                    print(f'Sending {i}')
                                    result = call_chatgpt(system_prompt, to_send, 300)
                                    print(f"Result: {result}")
                                    conv['Feedbacks'] = result
                                    i += 1
                    json.dump(source, output_file, indent=4)
                    output_file.write(',\n')
        output_file.write(']')

def refining_step():

    system_prompt = """
        You are an AI language model assistant specialized in classifying user prompts based on their structure.
        A "zero-shot" prompt contains an instruction or question without any examples.
        A "few-shot" prompt includes the instruction and one or more examples of the task.
        
        You have previously performed the task, and on the specific prompt that i will provide i have some feedback and suggestions
        that you could integrate into your reasoning. It is important to remember that the feedbacks and suggestions 
        provided has to integrate your reasoning, but you must not use only them to reach the outcome of the classification.
        **Task:**
        Given the user prompt below, perform the following steps:
                        
        1. Classification: Determine whether the prompt is "zero-shot" or "few-shot".
        2. Brief Reasoning: Provide a concise explanation for your classification in no more than 70 words.
                        
        **Output Format:**
                        
        - Classification: [Zero-shot/Few-shot]
        - Reasoning: [Your explanation and reasoning in 70 words or fewer]
    """

    with open('zero-few-iterations/dataset_prompt_step_3_v4.json', 'w') as output_file:
        output_file.write('[')
        with open('zero-few-iterations/dataset_prompt_step_2_v4.json', 'r') as f:
            data = json.load(f)
            i = 1
            for source in data:
                if source['TopicSoftwareDevelopmentAndEngineeringFlag']:
                    for block in source['ChatgptSharing']:
                        if block.get('Conversations', None) is not None:
                            for conv in block['Conversations']:
                                feedback = conv['Feedbacks']
                                if feedback.strip() != 'None':
                                    prompt = process_text(conv['Prompt'])
                                    to_send = f"""
                                    [FEEDBACKS_START]{feedback}[FEEDBACKS_END]
                                    [PROMPT_TO_ANALYZE_START]{prompt}[PROMPT_TO_ANALYZE_END]
                                    """
                                    print(f'Sending {i}')
                                    result = call_chatgpt(system_prompt, to_send, 300)
                                    print(f"Result: {result}")
                                    conv['Prompt_Pattern'] = result
                                    i += 1
                    json.dump(source, output_file, indent=4)
                    output_file.write(',\n')
        output_file.write(']')

if __name__ == '__main__':
    load_dotenv()
    #classification_step()
    feedback_step()
    #refining_step()
