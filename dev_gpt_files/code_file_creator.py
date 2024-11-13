import json
import os

# Dictionary to map code types/languages to their file extensions
extensions = {
    'python': 'py',
    'javascript': 'js',
    'typescript': 'ts',
    'java': 'java',
    'c++': 'cpp',
    'cpp': 'cpp',
    'c': 'c',
    'ruby': 'rb',
    'go': 'go',
    'tsx': 'tsx',
    'html': 'html',
    'css': 'css',
    'php': 'php',
    'swift': 'swift',
    'r': 'r',
    'sql': 'sql',
    'rust': 'rs',
    'svelte': 'svelte',
    'lua': 'lua',
    'js': 'js',
    'ts': 'ts',
    'groovy': 'groovy',
    'jsx': 'jsx',
    'csharp': 'cs',
    'scss': 'scss',
    'prisma': 'prisma',
    'kotlin': 'kt',
    'less': 'less',
    'perl': 'pl',
    'vue': 'vue'
}

# Function to load the JSON dataset from the provided file path
def load_dataset(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# Function to create files from code snippets in the dataset
def create_files_from_snippets(dataset):
    for source in dataset:
        # Only process sources flagged for software development and engineering
        if source['TopicSoftwareDevelopmentAndEngineeringFlag']:
            conv_id = source['Conversation_ID']
            i = 1
            for block in source['ChatgptSharing']:
                # Get conversation blocks if they exist
                blk_lst = block.get('Conversations', None)
                if blk_lst is not None:
                    # Iterate through each conversation in the block
                    for conv in blk_lst:
                        # Iterate through the list of code snippets in each conversation
                        for code in conv['ListOfCode']:
                            type = code['Type']
                            content = code['Content']

                            if type is not None and content is not None:
                                # Get the appropriate extension for the given type
                                extension = extensions.get(type.lower())

                                # Skip if the type is not supported
                                if not extension:
                                    print(f"Skipping snippet {conv_id}_{i} due to unsupported language '{type}'.")
                                else:
                                    # Create a folder for the specific extension if it doesn't exist
                                    folder_name = f"files/{extension}"
                                    os.makedirs(folder_name, exist_ok=True)

                                    # Create the file with a unique name in the appropriate folder
                                    file_name = f"{folder_name}/snippet_{conv_id}_{i}.{extension}"
                                    with open(file_name, 'w') as f:
                                        f.write(content)
                                    print(f"Created file: {file_name}")
                            # Increment the counter for snippet numbering
                            i += 1

# Function to count the number of code snippets in the dataset and track unique code types
def count(dataset):
    i = 0
    types = set()

    # Iterate through the dataset to count code snippets and track unique code types
    for source in dataset:
        if source['TopicSoftwareDevelopmentAndEngineeringFlag']:
            for block in source['ChatgptSharing']:
                blk_lst = block.get('Conversations', None)
                if blk_lst is not None:
                    for conv in blk_lst:
                        for code in conv['ListOfCode']:
                            type = code['Type']
                            # Track unique code types by adding them to the set
                            if type is not None:
                                types.add(type.lower())
                            # Increment the counter for code snippets
                            i += 1

    # Print the number of unique code types found
    print(len(types))
    return i

# Main function to load the dataset and call appropriate functions
if __name__ == "__main__":
    # Specify the path to your JSON dataset
    dataset_path = "dataset_prompt_step_3_v5.json"

    # Load the dataset and create filesT
    try:
        dataset = load_dataset(dataset_path)
        # Print the total number of code snippets found in the dataset
        print(count(dataset))
    except FileNotFoundError:
        print(f"Error: The file '{dataset_path}' was not found.")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON. Please check the format of the dataset.")
