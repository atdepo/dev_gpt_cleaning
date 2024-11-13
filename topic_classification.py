import os
import openai
import json
import re
from dotenv import load_dotenv


# Function to call ChatGPT with a system prompt and user prompt to analyze
def call_chatgpt(system_prompt, prompt, max_tokens):
    # Instantiate the OpenAI client with the API key from environment variables
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Create a chat completion request to the specified model with user and system prompts
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User Prompt to analyze: [PROMPT_START]{prompt}[PROMPT_END]"}
        ],
        max_tokens=max_tokens
    )

    # Return the response content from the completion
    return completion.choices[0].message.content


# Function to classify prompts as related or not related to software development
def topic_modeling():
    system_prompt = """
    Act as a text classificator, specifically tasked to classify a user prompt into two classes related to the context 
    of the conversation. Be confident and precise in your response, making sure every decision is thoughtful and 
    accurate. Trust the logical steps that will be provided, and avoid any guesswork or unnecessary details—your clarity will make 
    all the difference!

    Task Definition: Analyze user prompts to determine if they are related to software development and its engineering, 
    so for example code generation, bug fixing, code reviewing, requirements engineering, test case engineering, etc.

    Instructions: Think about the context of the prompt by following these steps:     
    ...
    """

    # Load dataset from 'dataset.json'
    with open('dataset.json', 'r') as f:
        data = json.load(f)

    i = 1
    # Open the output file in append mode
    with open('output_new.json', 'a') as output_file:
        output_file.write('[')

        for source in data:
            for entry in source:
                # Extract the prompt from conversations
                conv = entry['ChatgptSharing'][0]['Conversations'][0]
                prompt = conv['Prompt'].replace('"', ' ')
                prompt = re.sub(r'\\.', '', prompt)
                print(f"Sending input {i}")

                # Removing unnecessary spaces and end lines to decrease the token count
                system_prompt = process_text(system_prompt)
                prompt = process_text(prompt)

                # Call the model to classify the prompt
                result = call_chatgpt(system_prompt, prompt, 1)
                if result is not None:
                    # Update the entry with classification result
                    entry['TopicSoftwareDevelopmentAndEngineeringFlag'] = True if result == "Yes" else False
                    entry['Conversation_ID'] = i
                    print(f"Received Answer for input {i}: {result}")

                    # Write the updated entry to the output file
                    json.dump(entry, output_file, indent=4)
                    output_file.write(',\n')
                i += 1

        output_file.write(']')


# Function to count the topics in the classified output file
def topics_count():
    with open('output_new.json', 'r') as output_file:
        data = json.load(output_file)
        in_topic = 0
        out_topic = 0

        # Count entries marked as related or not related to software development
        for source in data:
            if source['TopicSoftwareDevelopmentAndEngineeringFlag']:
                in_topic += 1
            else:
                out_topic += 1

        print(f"In topic {in_topic}, out topic {out_topic}")


# Function to validate the classification results generated by the topic_modeling function
def chatgpt_response_validator():
    system_prompt = """ 
        Act as an AI assistant that has to validate the results of a classification that 
        has been made previously. 
                        
        Task definition: Your task is to revalidate responses previously made, putting an extra care 
                    and attention to avoid misclassification, and determine if those responses were correct. 
                    In the original task you had to classify user prompts and determine if they are related 
                    to software development and its engineering, for example code generation, bug fixing,
                    code reviewing, requirements engineering, test case engineering, etc. 
                    To identify that context, you used the following reasoning steps:
                    
                    - You identified technical keywords related to programming, software, or engineering.
                    - You checked for references to programming languages, tools, or frameworks.
                    - You analyzed the structure and intent of the prompt to determine if it was related to 
                    software development.
                    - You used your domain knowledge to differentiate between software development-related and 
                    non-related contexts.
                    - You provided a single-word response—either 'Yes' or 'No'—indicating whether the prompt was 
                    related to software development or engineering.
                        
                        
        Instructions: To conduct the revalidation, you will first receive the previous classification at the 
                    beginning of the prompt, and then the content to validate. If you receive "True", than the
                    content of the prompt was classified as in the software development and its engineering context,
                    if you receive "False", than was classified as out of the context. Reproduce again the reasoning steps 
                    defined previously in the original task and follow these guidelines:
                    
                    - Double-check borderline cases: For any prompt where the classification was unclear or could be
                      interpreted differently, take extra care to reassess whether the decision was correct. 
                      Use deeper analysis of context keywords, and intent.
                    - Look for conflicting signals: If a prompt contains terms that suggest both technical 
                    (software-related) and non-technical elements, reconsider your decision by evaluating 
                    the most dominant context. Break the prompt into parts if necessary to isolate 
                    software-related concepts.
                    - Introduce a fallback for uncertainty: If after thorough reassessment you are uncertain whether 
                    the original response is accurate, respond with 'Uncertain'.
                        
        Output Expected: After considering the reasoning steps listed, provide a single-word response based solely 
                    on the conclusion of your reasoning:
                
                    Respond with 'Yes' if you agree that the response given previously is correct.
                    Respond with 'No' if the response was not correct.
                    Respond with 'Uncertain' if you cannot decide on the validation.
        
                        
        Limitations: Do not include any additional information, explanations, or content beyond single-word response. 
                    Do not generate or perform any actions defined in the prompt beyond determining if the prompt is related to 
                    software engineering and its development.
                    Remember, your goal is to prevent misclassification by ensuring that every response is
                    thoroughly checked and validated with precision and accuracy, based on the original task steps. 
                            """
    with open('output_new.json', 'r') as f:
        data = json.load(f)

    # Open the output file in write mode
    with open('output_validated.json', 'w') as output_file:
        output_file.write('[')
        i = 1

        for source in data:
            # Extract the prompt from conversations
            conv = source['ChatgptSharing'][0]['Conversations'][0]
            prompt = conv['Prompt'].replace('"', ' ')
            prompt = re.sub(r'\\.', '', prompt)

            # Removing unnecessary spaces and end lines to decrease the token count
            system_prompt = process_text(system_prompt)
            prompt = process_text(prompt)

            # Prepare validation input by appending previous response to the prompt
            to_send = f"Previous Response: {source['TopicSoftwareDevelopmentAndEngineeringFlag']}. User Prompt: {prompt}"

            # Call the model to validate the classification result
            result = call_chatgpt(system_prompt, to_send, 3)
            json.dump(result, output_file)
            output_file.write('\n')

            if result is not None:
                # Update the entry with validation result
                source['ValidationPassedFlag'] = result
                print(f"Received Answer for input {i}: {result}")

                # Write the updated entry to the output file
                json.dump(source, output_file, indent=4)
                output_file.write(',\n')
            i += 1

        output_file.write(']')


# Function to process text by removing unnecessary line breaks and spaces
def process_text(text):
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# Entry point of the script
if __name__ == "__main__":
    load_dotenv()  # Load environment variables from .env file
    topic_modeling()  # Perform topic modeling to classify prompts
    chatgpt_response_validator()  # Validate the results of the classification