import json
import os
import re
from sonarqube import SonarQubeClient
from dotenv import load_dotenv


def retrieve():
    sonar = SonarQubeClient(sonarqube_url="http://localhost:9000", username=os.getenv("USER"), password=os.getenv("PASSWORD"))
    issue_list = []
    page_idx = 1
    page_size = 500
    end_cond = False

    while not end_cond:
        issues = sonar.issues.search_issues(componentKeys="paper-quality-final", ps=page_size, p=page_idx)
        issue_list = issue_list + issues['issues']
        page_idx += 1
        end_cond = not len(issues['issues']) == page_size

    with open('issues.json', 'w') as output_file:
        json.dump(issue_list, output_file, indent=4)


def add_quality_metrics_json():
    with open('dataset_prompt_step_3_v5.json', 'r') as dataset_file:
        json_data = json.load(dataset_file)

        with open('issues.json', 'r') as input_file:
            data = json.load(input_file)
            for source in json_data:
                if source['TopicSoftwareDevelopmentAndEngineeringFlag']:
                    conv_id = source['Conversation_ID']
                    i = 1
                    for block in source['ChatgptSharing']:
                        blk_lst = block.get('Conversations', None)
                        if blk_lst is not None:
                            for conv in blk_lst:
                                for code in conv['ListOfCode']:
                                    quality_meas = []
                                    snip = get_snippet(data, conv_id, i)
                                    for el in snip:
                                        for imp in el["impacts"]:
                                            val = {"type": el["type"], "dimension": imp["softwareQuality"], "severity": imp["severity"]}
                                            quality_meas.append(val)
                                    if len(quality_meas) > 0:
                                        code["QualityMeasurement"] = quality_meas
                                    code["Snippet_ID"] = f"{conv_id}_{i}"
                                    if f"{conv_id}_{i}" == "1712_3":
                                        print("t")
                                    i += 1

    with open('outcome_step_1.json', 'w') as f:
        json.dump(json_data, f, indent=4)


def get_snippet(data, i, j):

    snip = []
    for elem in data:
        coords = elem['component'].split("/")[1].split(".")[0].split("_")[1:3]

        if int(coords[0]) == i and int(coords[1]) == j and elem["message"] != "A parsing error occurred in this file.":
            snip.append(elem)
    return snip


def prompt_patterns_join():

    with open('outcome_step_1.json', 'r') as f:
        data = json.load(f)
        for source in data:
            if source['TopicSoftwareDevelopmentAndEngineeringFlag']:
                for block in source['ChatgptSharing']:
                    blk_lst = block.get('Conversations', None)
                    if blk_lst is not None:
                        for conv in blk_lst:
                            pattern = r'Classification:\s*(.*)'

                            zero_few = conv.get('Prompt_Pattern')
                            cot = conv.get('Prompt_Pattern_CoT')
                            personas = conv.get('Prompt_Pattern_Personas')

                            match = re.search(pattern=pattern, string=zero_few)
                            s1 = match.group(1).strip()
                            match = re.search(pattern=pattern, string=cot)
                            s2 = match.group(1).strip()
                            match = re.search(pattern=pattern, string=personas)
                            s3 = match.group(1).strip()

                            prompt_pattern = ";".join([s1, s2, s3])
                            conv['Prompt_Pattern'] = prompt_pattern
                            conv.pop('Prompt_Pattern_CoT')
                            conv.pop('Prompt_Pattern_Personas')
                            conv.pop('Feedbacks')

    with open('outcome_step_2.json', 'w') as f:
        json.dump(data, f, indent=4)

def build_json_file_errors():
    # List of error messages to check
    errors = ["Failed to build control flow graph in file", "Unable to analyze file",
              "Cannot parse", "Failed to parse file", "Occurred while linting"]

    # Regular expression pattern to find the filename (e.g., snippet_xx_yy.zz)
    filename_pattern = r'snippet_\d+_\d+\.(\w+)'

    # Dictionary to store errors by programming language
    error_log_by_language = {}

    # Mapping of file extensions to programming languages
    extension_to_language = {
        'py': 'Python',
        'js': 'JavaScript',
        'ts': 'TypeScript',
        'java': 'Java',
        'cpp': 'C++',
        'c': 'C',
        'rb': 'Ruby',
        'go': 'Go',
        'tsx': 'TypeScript (React)',
        'html': 'HTML',
        'css': 'CSS',
        'php': 'PHP',
        'swift': 'Swift',
        'r': 'R',
        'sql': 'SQL',
        'rs': 'Rust',
        'svelte': 'Svelte',
        'lua': 'Lua',
        'groovy': 'Groovy',
        'jsx': 'JavaScript (React)',
        'cs': 'C#',
        'scss': 'SCSS',
        'prisma': 'Prisma',
        'kt': 'Kotlin',
        'less': 'LESS',
        'pl': 'Perl',
        'vue': 'Vue'
    }

    # Open and read the log file line by line
    with open('files/log.txt', 'r') as f:
        for line in f:
            # Check if the line contains any of the error messages
            for error in errors:
                if error in line:
                    # Search for the filename pattern in the line
                    match = re.search(filename_pattern, line)
                    if match:
                        # Extract the filename and the file extension
                        filename = match.group(0)
                        extension = match.group(1)

                        # Identify the programming language from the extension
                        language = extension_to_language.get(extension, "Unknown")

                        # Initialize the list for the language if not already present
                        if language not in error_log_by_language:
                            error_log_by_language[language] = []

                        # Append the filename to the language-specific list if it's not already present
                        if filename not in error_log_by_language[language]:
                            error_log_by_language[language].append(filename)
                        else:
                            print(f"Duplicate found: {filename} in {language}")
                    break  # Stop searching once an error is found in the line

    # Write the categorized error log to a JSON file
    with open('error_log_by_language.json', 'w') as json_file:
        json.dump(error_log_by_language, json_file, indent=4)

    print("Error log saved to 'error_log_by_language.json'")


def add_errors_json():

    with open('error_log_by_language.json', 'r') as f:
        error_log_by_language = json.load(f)

    with open('outcome_step_2.json', 'r') as input_file:
        data = json.load(input_file)
        for source in data:
            if source['TopicSoftwareDevelopmentAndEngineeringFlag']:
                for block in source['ChatgptSharing']:
                    blk_lst = block.get('Conversations', None)
                    if blk_lst is not None:
                        for conv in blk_lst:
                            for code in conv['ListOfCode']:
                               name = code["Snippet_ID"]
                               is_error = get_error(error_log_by_language, name)
                               if is_error:
                                   code["QualityMeasurement"] = {"type":"Compilation error during analysis", "dimension": None, "severity": None}


        with open('outcome_step_3.json', 'w') as f:
            json.dump(data, f, indent=4)

def get_error(data, name):
    for elem in data.values():
        for string in elem:
            if string.split(".")[0] == f"snippet_{name}":
                return True

    return False

if __name__ == '__main__':
    load_dotenv()
    #retrieve()
    add_quality_metrics_json()
    prompt_patterns_join()
    build_json_file_errors()
    add_errors_json()

