import json
from topic_modeler import process_text, call_chatgpt
from dotenv import load_dotenv


def zero_few_shot_patterns():
    system_prompt = """
        Definitions:

        Zero-Shot Prompt: A prompt that provides instructions or asks a question without any examples demonstrating how to perform the task.
        Few-Shot Prompt: A prompt that includes one or more examples demonstrating how the task should be performed before requesting a response.
        Instructions:

        Read the User Prompt Carefully:
        Examine the entire prompt that i will provide you for any content that serves as an example or demonstration of how to perform the task.
        Identify Examples:
        Look for Demonstrations: Check if the prompt contains explicit or implicit examples that illustrate the method or steps to accomplish the task. Examples are intended to guide the approach to the task.
        Distinguish from Content to be Processed: Recognize that code snippets, data, or text provided as content to be worked on are not examples if they don't demonstrate how to perform the task but are instead the subject of the task.
        Classify the Prompt:
        Few-Shot: If one or more examples demonstrating the method or steps to perform the task are present, classify the prompt as "Few-Shot."
        Zero-Shot: If no such examples are present, and the prompt only contains instructions and/or content to be processed, classify the prompt as "Zero-Shot."
        Formatting Tips for Identifying Examples:
        Examples often appear after phrases like “For example,” “e.g.,” or are presented in code blocks or lists that illustrate the approach.
        Be aware that examples are meant to instruct on the method, not just provide material to work on. 
        Examples like embedded commands or URLs also qualify as examples if they demonstrate expected behavior or outputs. 
        Be critical when assessing the meaning of the example piece, if it is only code, commands pasted to be refactored
        or errors to be addressed, or if they are informative examples of how to perform a task and accomplish the result
        Provide the Answer:

        Simply state "Zero-Shot" or "Few-Shot" as your final answer.
        Ensure the answer is clear and free of any additional text.
        """

    with open('datasets/dataset_prompt_step_1.json', 'w') as output_file:
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
                                result = call_chatgpt(system_prompt, prompt, 5)
                                print(f"Result: {result}")
                                conv['Prompt_Pattern'] = result
                                i += 1
                    json.dump(source, output_file, indent=4)
                    output_file.write(',\n')
        output_file.write(']')


if __name__ == '__main__':
    load_dotenv()
    zero_few_shot_patterns()
