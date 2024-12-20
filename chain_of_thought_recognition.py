import json
from topic_classification import process_text, call_chatgpt
from dotenv import load_dotenv


# Function to classify user prompts as "Chain of Thought" (CoT) or not
def classification_step():
    system_prompt = """
                You are an AI language model assistant specialized in classifying user prompts based on their structure. A "Chain of Thought" (CoT) prompt encourages the model to solve problems by breaking them down step-by-step, often using intermediate logical steps and clear reasoning connectors.

                Task: Given the user prompt below, perform the following steps:

                Classification: Determine whether the prompt follows a "Chain of Thought" (CoT) structure.
                Brief Reasoning: Provide a concise explanation for your classification in no more than 70 words.
                Output Format:

                Classification: [Chain of Thought/Not Chain of Thought]
                Reasoning: [Your explanation and reasoning in 70 words or fewer]"""

    # List to store the classification results
    results = []

    # Open the input dataset file
<<<<<<<< Updated upstream:dev_gpt_files/chain_of_thought_classification.py
    with open('zero-few-iterations/dataset_prompt_step_3_v5.json', 'r') as f:  # Start from the last
========
    with open('zero-few-iterations/dataset_prompt_step_2_v5.json', 'r') as f:  # Start from the last
>>>>>>>> Stashed changes:chain_of_thought_recognition.py
        data = json.load(f)
        i = 1
        for source in data:
            if source['TopicSoftwareDevelopmentAndEngineeringFlag']:
                for block in source['ChatgptSharing']:
                    if block.get('Conversations', None) is not None:
                        # Iterate over each conversation in the block
                        for conv in block['Conversations']:
                            # Process the prompt to remove unnecessary whitespace
                            prompt = process_text(conv['Prompt'])
                            print(f'Sending {i}')

                            # Get classification result using call_chatgpt function
                            result = call_chatgpt(system_prompt, prompt, 200)
                            print(f"Result: {result}")

                            # Store the classification result in the conversation dictionary
                            conv['Prompt_Pattern_CoT'] = result
                            i += 1
                results.append(source)

    # Save classification results to output file
    with open(f'cot-iterations/dataset_prompt_step_1_v1.json', 'w') as output_file:
        json.dump(results, output_file, indent=4)


# Function to provide feedback on the CoT classification step
def feedback_step(j):
    system_prompt = """
            Role: You are an expert linguist and text classifier with extensive experience in nuanced text analysis.

            Task: Please review the following text and the previous classification along with its reasoning. Your goal is to evaluate the accuracy and completeness of the classification.
            
            Instructions:
            
            Evaluation:
            Think step by step about the key points of the Chain of Thought (CoT) prompting pattern, its main characteristics, and composition.
            Determine whether the classification accurately reflects the content of the text, also using the previous reasoning to further understand how such classification was produced.
            Assess the correctness provided for the classification. Read again your answer if you are not sure, be critical.
            Do not infer anything that is not written in the prompt, focus solely on the content.
            Feedback:
            If you agree with the classification or you think that the classification is accurate, and have no feedback or suggestions, output "None". If your only feedback relies on strengthening the reasoning or the fact that the reasoning could have included more detail, also output "None."
            If you disagree or see areas for improvement, identify the errors, misclassifications, and overlooked aspects. Give as an output feedback on the reasoning produced and suggestions on areas to explore further to refine the classification. For example, if you notice that the classification has not recognized logical steps or explicit intermediate breakdowns required for CoT, make it clear in the feedback and suggestion part.
            Response Format if you disagree: Feedback:
            
            [Feedback point 1 (at most 70 words)]
            [Feedback point 2 (at most 70 words)]
            Suggestions:
            
            [Suggestion 1 (at most 70 words)]
            [Suggestion 2 (at most 70 words)]
            Response Format if you agree: None"""

    # List to store the feedback results
    results = []

<<<<<<<< Updated upstream:dev_gpt_files/chain_of_thought_classification.py
    read_file = ""
    if idx == 1:
        read_file = "cot-iterations/dataset_prompt_step_1_v1.json"
    else:
        read_file = f'cot-iterations/dataset_prompt_step_3_v{j - 1}.json'

    # Open the dataset for feedback step
    with open(read_file, 'r') as f:
========
    # Open the dataset for feedback step
    with open(f'cot-iterations/dataset_prompt_step_3_v{j - 1}.json', 'r') as f:
>>>>>>>> Stashed changes:chain_of_thought_recognition.py
        data = json.load(f)
        i = 1
        for source in data:
            if source['TopicSoftwareDevelopmentAndEngineeringFlag']:
                for block in source['ChatgptSharing']:
                    if block.get('Conversations', None) is not None:
                        # Iterate over each conversation in the block
                        for conv in block['Conversations']:
                            feedback = conv.get('Feedbacks', 'None')
                            if feedback != 'None':
                                # Process the prompt to remove unnecessary whitespace
                                prompt = process_text(conv['Prompt'])
                                res = conv['Prompt_Pattern_CoT']

                                # Filter lines related to classification and reasoning
                                filtered_lines = [line for line in res.split('\n') if
                                                  line.startswith("Classification") or line.startswith("Reasoning")]
                                if len(filtered_lines) < 2:
                                    conv['Feedbacks'] = "ERROR"
                                else:
                                    # Prepare input for feedback
                                    to_send = f"""
                                    [CLASSIFICATION_START]{filtered_lines[0]}[CLASSIFICATION_END]
                                    [REASONING_START]{filtered_lines[1]}[REASONING_END]
                                    [PROMPT_ANALYZED_START]{prompt}[PROMPT_ANALYZED_END]
                                    """
                                    print(f'Sending {i}')

                                    # Get feedback result using call_chatgpt function
                                    result = call_chatgpt(system_prompt, to_send, 300)
                                    print(f"Result: {result}")
                                    conv['Feedbacks'] = result
                                i += 1
                results.append(source)

    # Save feedback results to output file
    with open(f'cot-iterations/dataset_prompt_step_2_v{j}.json', 'w') as output_file:
        json.dump(results, output_file, indent=4)


# Function to refine CoT classification based on the feedback provided
def refinement_step(j):
    system_prompt = """
            You are an AI language model assistant specialized in classifying user prompts based on their structure. A "Chain of Thought" (CoT) prompt encourages the model to solve problems by breaking them down step-by-step, often using intermediate logical steps and clear reasoning connectors.
        
            You have previously performed the task, and on the specific prompt that I will provide, I have some feedback and suggestions that you could integrate into your reasoning. It is important to remember that the feedback and suggestions provided are to help you refine your reasoning, but you must not use only them to reach the outcome of the classification.
            
            Task: Given the user prompt below, perform the following steps:
            
            Classification: Determine whether the prompt follows a "Chain of Thought" (CoT) structure.
            Brief Reasoning: Provide a concise explanation for your classification in no more than 70 words.
            Output Format:
            
            Classification: [Chain of Thought/Not Chain of Thought]
            Reasoning: [Your explanation and reasoning in 70 words or fewer]"""

    # List to store the refinement results
    results = []

    # Open the dataset for the refinement step
    with open(f'cot-iterations/dataset_prompt_step_2_v{j}.json', 'r') as f:
        data = json.load(f)
        i = 1
        for source in data:
            if source['TopicSoftwareDevelopmentAndEngineeringFlag']:
                for block in source['ChatgptSharing']:
                    if block.get('Conversations', None) is not None:
                        # Iterate over each conversation in the block
                        for conv in block['Conversations']:
                            feedback = conv['Feedbacks']
                            if feedback.strip() != 'None':
                                # Process the prompt to remove unnecessary whitespace
                                prompt = process_text(conv['Prompt'])

                                # Prepare input for refining classification based on feedback
                                to_send = f"""
                                [FEEDBACKS_START]{feedback}[FEEDBACKS_END]
                                [PROMPT_TO_ANALYZE_START]{prompt}[PROMPT_TO_ANALYZE_END]
                                """
                                print(f'Sending {i}')

                                # Get refined classification using call_chatgpt function
                                result = call_chatgpt(system_prompt, to_send, 300)
                                print(f"Result: {result}")
                                conv['Prompt_Pattern_CoT'] = result
                                i += 1
                results.append(source)

    # Save refinement results to output file
    with open(f'cot-iterations/dataset_prompt_step_3_v{j}.json', 'w') as output_file:
        json.dump(results, output_file, indent=4)


# Entry point of the script
if __name__ == '__main__':
    load_dotenv()  # Load environment variables from .env file

    # Run classification step to classify prompts as CoT or not
    classification_step()

    # Iterate through feedback and refinement steps
    idx = 1
    while idx <= 5:
        feedback_step(idx)  # Provide feedback for the current iteration
        refinement_step(idx)  # Refine classification based on the feedback
        idx += 1
