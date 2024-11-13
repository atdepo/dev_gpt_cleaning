import json
from topic_classification import process_text, call_chatgpt
from dotenv import load_dotenv


# Function to classify user prompts as either "zero-shot" or "few-shot"
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

    # Open output file in write mode to save the classification results
    with open('zero-few-iterations/dataset_prompt_step_1_v1.json', 'w') as output_file:
        output_file.write('[')

        # Open and read input dataset file
        with open('../datasets/output_filtered.json', 'r') as f:
            data = json.load(f)
            i = 1

            # Iterate over each source in the dataset
            for source in data:
                if source['TopicSoftwareDevelopmentAndEngineeringFlag']:
                    # Iterate over ChatGPT conversation blocks
                    for block in source['ChatgptSharing']:
                        if block.get('Conversations', None) is not None:
                            # Iterate over conversations in each block
                            for conv in block['Conversations']:
                                # Process the prompt to remove unnecessary whitespace
                                prompt = process_text(conv['Prompt'])
                                print(f'Sending {i}')

                                # Classify the prompt using the call_chatgpt function
                                result = call_chatgpt(system_prompt, prompt, 200)
                                print(f"Result: {result}")

                                # Store the classification result in the conversation dictionary
                                conv['Prompt_Pattern'] = result
                                i += 1

                    # Write the updated source back to the output file
                    json.dump(source, output_file, indent=4)
                    output_file.write(',\n')
        output_file.write(']')


# Function to validate the classification results and provide feedback if necessary
def feedback_step(idx):
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

    # Open output file in write mode to save the feedback results
    with open(f'zero-few-iterations/dataset_prompt_step_2_v{idx}.json', 'w') as output_file:
        output_file.write('[')

        read_file = ""
        if idx == 1:
            read_file = "output_validated.json"
        else:
            read_file = f'zero-few-iterations/dataset_prompt_step_3_v{idx-1}.json'
        # Open and read input dataset file
        with open(read_file, 'r') as f:
            data = json.load(f)
            i = 1

            # Iterate over each source in the dataset
            for source in data:
                if source['TopicSoftwareDevelopmentAndEngineeringFlag']:
                    # Iterate over ChatGPT conversation blocks
                    for block in source['ChatgptSharing']:
                        if block.get('Conversations', None) is not None:
                            # Iterate over conversations in each block
                            for conv in block['Conversations']:
                                feedback = conv.get('Feedbacks', 'None')
                                if feedback != 'None':
                                    # Process the prompt to remove unnecessary whitespace
                                    prompt = process_text(conv['Prompt'])
                                    res = conv['Prompt_Pattern']
                                    classification, reasoning = res.split('\n')

                                    # Prepare input for feedback validation by including classification and reasoning
                                    to_send = f"""
                                    [CLASSIFICATION_START]{classification}[CLASSIFICATION_END]
                                    [REASONING_START]{reasoning}[REASONING_END]
                                    [PROMPT_ANALYZED_START]{prompt}[PROMPT_ANALYZED_END]
                                    """
                                    print(f'Sending {i}')

                                    # Get feedback from the model using call_chatgpt function
                                    result = call_chatgpt(system_prompt, to_send, 300)
                                    print(f"Result: {result}")

                                    # Store the feedback result in the conversation dictionary
                                    conv['Feedbacks'] = result
                                    i += 1

                    # Write the updated source back to the output file
                    json.dump(source, output_file, indent=4)
                    output_file.write(',\n')
        output_file.write(']')


# Function to refine classification results based on feedback received
def refining_step(idx):
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

    # Open output file in write mode to save the refined results
    with open(f'zero-few-iterations/dataset_prompt_step_3_v{idx}.json', 'w') as output_file:
        output_file.write('[')

        # Open and read input dataset file
        with open(f'zero-few-iterations/dataset_prompt_step_2_v{idx}.json', 'r') as f:
            data = json.load(f)
            i = 1

            # Iterate over each source in the dataset
            for source in data:
                if source['TopicSoftwareDevelopmentAndEngineeringFlag']:
                    # Iterate over ChatGPT conversation blocks
                    for block in source['ChatgptSharing']:
                        if block.get('Conversations', None) is not None:
                            # Iterate over conversations in each block
                            for conv in block['Conversations']:
                                feedback = conv['Feedbacks']
                                if feedback.strip() != 'None':
                                    # Process the prompt to remove unnecessary whitespace
                                    prompt = process_text(conv['Prompt'])

                                    # Prepare input for refining the classification by including feedback
                                    to_send = f"""
                                    [FEEDBACKS_START]{feedback}[FEEDBACKS_END]
                                    [PROMPT_TO_ANALYZE_START]{prompt}[PROMPT_TO_ANALYZE_END]
                                    """
                                    print(f'Sending {i}')

                                    # Refine the classification result based on feedback using call_chatgpt function
                                    result = call_chatgpt(system_prompt, to_send, 300)
                                    print(f"Result: {result}")

                                    # Store the refined classification result in the conversation dictionary
                                    conv['Prompt_Pattern'] = result
                                    i += 1

                    # Write the updated source back to the output file
                    json.dump(source, output_file, indent=4)
                    output_file.write(',\n')
        output_file.write(']')


# Entry point of the script
if __name__ == '__main__':
    load_dotenv()  # Load environment variables from .env file
    classification_step()
    # Iterate through feedback and refinement steps
    idx = 1
    while idx <= 5:
        feedback_step(idx)
        refining_step(idx)
        idx += 1
