import json
import os

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


# Load the JSON dataset
def load_dataset(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


# Create files based on the Type and Code fields
def create_files_from_snippets(dataset):
    for source in dataset:
        if source['TopicSoftwareDevelopmentAndEngineeringFlag']:
            conv_id = source['Conversation_ID']
            i = 1
            for block in source['ChatgptSharing']:
                blk_lst = block.get('Conversations', None)
                if blk_lst is not None:
                    for conv in blk_lst:
                        for code in conv['ListOfCode']:
                            type = code['Type']
                            content = code['Content']

                            if type is not None and content is not None:
                                # Create a file with the appropriate extension
                                extension = extensions.get(type.lower())
                                if not extension:
                                    print(f"Skipping snippet {conv_id}_{i} due to unsupported language '{type}'.")
                                else:
                                    # Create a folder for the specific extension if it doesn't exist
                                    folder_name = f"files/{extension}"
                                    os.makedirs(folder_name, exist_ok=True)

                                    # Create the file within the appropriate folder
                                    file_name = f"{folder_name}/snippet_{conv_id}_{i}.{extension}"
                                    with open(file_name, 'w') as f:
                                        f.write(content)
                                    print(f"Created file: {file_name}")
                            i += 1


if __name__ == "__main__":
    # Specify the path to your JSON dataset
    dataset_path = "dataset_prompt_step_3_v5.json"

    # Load the dataset and create files
    try:
        dataset = load_dataset(dataset_path)
        create_files_from_snippets(dataset)
    except FileNotFoundError:
        print(f"Error: The file '{dataset_path}' was not found.")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON. Please check the format of the dataset.")