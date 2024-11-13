import json
import re
from sonarqube import SonarQubeClient
from collections import Counter
import csv
import os
from statistics import mean, median
from dotenv import load_dotenv

# Mapping of file extensions to programming languages
extension_to_language = {
    'python': 'py',
    'javascript': 'js',
    'typescript': 'ts',
    # 'java': 'java',  # Uncomment to add Java
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

# Function to retrieve SonarQube quality metrics for issues
def retrieve():
    # Connect to SonarQube with credentials
    sonar = SonarQubeClient(sonarqube_url="http://localhost:9000", username=os.getenv("username"), password=os.getenv("password"))
    issue_list = []
    page_idx = 1
    page_size = 500
    end_cond = False

    # Paginate through issues until no more pages are found
    while not end_cond:
        issues = sonar.issues.search_issues(componentKeys="paper-quality-final", ps=page_size, p=page_idx)
        issue_list = issue_list + issues['issues']
        page_idx += 1
        end_cond = not len(issues['issues']) == page_size

    # Save the retrieved issues to 'issues.json'
    with open('issues.json', 'w') as output_file:
        json.dump(issue_list, output_file, indent=4)

# Function to add quality metrics to JSON dataset
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
                            # Iterate over each code snippet in the conversation
                            for conv in blk_lst:
                                for code in conv['ListOfCode']:
                                    quality_meas = []
                                    snip = get_snippet(data, conv_id, i)
                                    # Extract quality measurement from issues data
                                    for el in snip:
                                        for imp in el["impacts"]:
                                            val = {"type": el["type"], "dimension": imp["softwareQuality"], "severity": imp["severity"]}
                                            quality_meas.append(val)
                                    if len(quality_meas) > 0:
                                        code["QualityMeasurement"] = quality_meas
                                    code["Snippet_ID"] = f"{conv_id}_{i}"
                                    i += 1

    # Save updated dataset to 'outcome_step_1.json'
    with open('outcome_step_1.json', 'w') as f:
        json.dump(json_data, f, indent=4)

# Helper function to get relevant snippet data from SonarQube issues
def get_snippet(data, i, j):
    snip = []
    # Iterate over issues and check if they match the current snippet ID
    for elem in data:
        coords = elem['component'].split("/")[1].split(".")[0].split("_")[1:3]
        if int(coords[0]) == i and int(coords[1]) == j and elem["message"] != "A parsing error occurred in this file.":
            snip.append(elem)
    return snip

# Function to join prompt patterns into a unified structure
def prompt_patterns_join():
    with open('outcome_step_1.json', 'r') as f:
        data = json.load(f)
        for source in data:
            if source['TopicSoftwareDevelopmentAndEngineeringFlag']:
                for block in source['ChatgptSharing']:
                    blk_lst = block.get('Conversations', None)
                    if blk_lst is not None:
                        for conv in blk_lst:
                            # Extract classification results from each of the prompt patterns
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

                            # Join the classification results into a single prompt pattern
                            prompt_pattern = ";".join([s1, s2, s3])
                            conv['Prompt_Pattern'] = prompt_pattern

                            # Remove unnecessary fields
                            conv.pop('Prompt_Pattern_CoT')
                            conv.pop('Prompt_Pattern_Personas')
                            conv.pop('Feedbacks')

    # Save the result to 'outcome_step_2.json'
    with open('outcome_step_2.json', 'w') as f:
        json.dump(data, f, indent=4)

# Function to categorize errors by programming language
def build_json_file_errors():
    errors = ["Failed to build control flow graph in file", "Unable to analyze file", "Cannot parse", "Failed to parse file", "Occurred while linting"]
    filename_pattern = r'snippet_\d+_\d+\.(\w+)'
    error_log_by_language = {}

    # Open and read log file to identify errors
    with open('files/log.txt', 'r') as f:
        for line in f:
            for error in errors:
                if error in line:
                    match = re.search(filename_pattern, line)
                    if match:
                        filename = match.group(0)
                        extension = match.group(1)
                        language = extension_to_language.get(extension, "Unknown")
                        if language not in error_log_by_language:
                            error_log_by_language[language] = []
                        if filename not in error_log_by_language[language]:
                            error_log_by_language[language].append(filename)
                        else:
                            print(f"Duplicate found: {filename} in {language}")
                    break

    # Save the categorized error log to 'error_log_by_language.json'
    with open('error_log_by_language.json', 'w') as json_file:
        json.dump(error_log_by_language, json_file, indent=4)

    print("Error log saved to 'error_log_by_language.json'")

# Function to add errors to the JSON dataset
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
                                    # Add error information to QualityMeasurement
                                    code["QualityMeasurement"] = [{"type": "Compilation error during analysis", "dimension": None, "severity": None}]

    # Save the final dataset to 'final_dataset.json'
    with open('final_dataset.json', 'w') as f:
        json.dump(data, f, indent=4)

# Helper function to check if a code snippet has an error
def get_error(data, name):
    for elem in data.values():
        for string in elem:
            if string.split(".")[0] == f"snippet_{name}":
                return True
    return False

def create_csv():
    with open('outcome_step_3.json', 'r') as file:
        data = json.load(file)
        with open('issue_counts.csv', mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=';')

            # Write header row
            csv_writer.writerow(["SNIPPET_ID", "PROMPT_PATTERN", "MAINTAINABILITY", "SECURITY", "RELIABILITY"])
            patterns = {
                "Zero-shot;Not Chain of Thought;Not Personas Pattern": "Zero-shot",
                "Zero-shot;Chain of Thought;Not Personas Pattern": "Zero-shot with CoT",
                "Zero-shot;Not Chain of Thought;Personas Pattern": "Zero-shot with Personas",
                "Zero-shot;Chain of Thought;Personas Pattern": "Zero-shot with CoT and Personas",
                "Few-shot;Not Chain of Thought;Not Personas Pattern": "Few-shot",
                "Few-shot;Chain of Thought;Not Personas Pattern": "Few-shot with CoT",
                "Few-shot;Not Chain of Thought;Personas Pattern": "Few-shot with Personas",
                "Few-shot;Chain of Thought;Personas Pattern": "Few-shot with CoT and Personas"
            }

            failed = 0
            for source in data:
                if not source.get('TopicSoftwareDevelopmentAndEngineeringFlag'):
                    continue

                for block in source.get('ChatgptSharing', []):
                    blk_lst = block.get('Conversations', [])
                    for conv in blk_lst:
                        pp = conv.get("Prompt_Pattern")
                        pattern = patterns.get(pp, None)

                        for code in conv.get("ListOfCode", []):

                            file_type = code.get('Type')
                            content = code.get('Content')
                            snippet_id = code.get("Snippet_ID")

                            if file_type is not None and content is not None:

                                extension = extension_to_language.get(file_type.lower())
                                if not extension:
                                    continue

                                qm = code.get("QualityMeasurement", None)

                                # Skip code blocks with compilation errors
                                if qm and qm[0].get("type") == "Compilation error during analysis":
                                    failed += 1
                                    continue

                                # Determine counts of each metric
                                if qm:
                                    type_counter = Counter(item["dimension"] for item in qm)
                                else:
                                    type_counter = Counter()

                                maintainability_count = type_counter.get("MAINTAINABILITY", 0)
                                security_count = type_counter.get("SECURITY", 0)
                                reliability_count = type_counter.get("RELIABILITY", 0)

                                # Write the data to CSV
                                csv_writer.writerow(
                                    [snippet_id, pattern, maintainability_count, security_count, reliability_count])
            print(failed)


# Function to create a CSV with metrics from the JSON dataset
def create_csv_2():
    with open('final_dataset.json', 'r') as file:
        data = json.load(file)
        with open('conv_counts_v2.csv', mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=';')

            # Write header row
            csv_writer.writerow(["CONVERSATION_ID", "CONVERSATION_COUNT", "MAINTAINABILITY_MEAN", "SECURITY_MEAN", "RELIABILITY_MEAN", "MAINTAINABILITY_MEDIAN", "SECURITY_MEDIAN", "RELIABILITY_MEDIAN"])
            for source in data:
                if not source.get('TopicSoftwareDevelopmentAndEngineeringFlag'):
                    continue
                conv_id = source.get("Conversation_ID")
                counter_array = []
                conv_counter = 0
                for block in source.get('ChatgptSharing', []):
                    blk_lst = block.get('Conversations', [])
                    for conv in blk_lst:
                        conv_counter += 1

                        for code in conv.get("ListOfCode", []):
                            file_type = code.get('Type')
                            content = code.get('Content')

                            if file_type is not None and content is not None:
                                extension = extension_to_language.get(file_type.lower())
                                if not extension:
                                    continue

                                qm = code.get("QualityMeasurement", None)
                                # Skip code blocks with compilation errors
                                if qm and qm[0].get("type") == "Compilation error during analysis":
                                    continue

                                # Count metrics for each quality dimension
                                if qm:
                                    counter_array.append(Counter(item["dimension"] for item in qm))

                # Calculate and write mean and median metrics to CSV
                if conv_counter > 1:
                    counts_main = [counter["MAINTAINABILITY"] for counter in counter_array]
                    counts_sec = [counter["SECURITY"] for counter in counter_array]
                    counts_rel = [counter["RELIABILITY"] for counter in counter_array]

                    mean_main, mean_sec, mean_rel = 0, 0, 0
                    if len(counts_main) > 0:
                        mean_main = mean(counts_main)
                    if len(counts_sec) > 0:
                        mean_sec = mean(counts_sec)
                    if len(counts_rel) > 0:
                        mean_rel = mean(counts_rel)

                    median_main, median_sec, median_rel = 0, 0, 0
                    if len(counts_main) > 0:
                        median_main = median(counts_main)
                    if len(counts_sec) > 0:
                        median_sec = median(counts_sec)
                    if len(counts_rel) > 0:
                        median_rel = median(counts_rel)

                    csv_writer.writerow([conv_id, conv_counter, mean_main, mean_sec, mean_rel, median_main, median_sec, median_rel])
                elif len(counter_array) > 0:
                    elem = counter_array[0]
                    csv_writer.writerow([conv_id, conv_counter, elem.get("MAINTAINABILITY", 0), elem.get("SECURITY", 0), elem.get("RELIABILITY", 0), elem.get("MAINTAINABILITY", 0), elem.get("SECURITY", 0), elem.get("RELIABILITY", 0)])
                else:
                    csv_writer.writerow([conv_id, conv_counter, 0, 0, 0, 0, 0, 0])

# Entry point of the script
if __name__ == '__main__':
    load_dotenv()  # Load environment variables
    retrieve()  # Retrieve quality metrics from SonarQube
    add_quality_metrics_json()  # Add quality metrics to dataset
    prompt_patterns_join()  # Join prompt patterns into unified structure
    build_json_file_errors()  # Categorize errors by programming language
    add_errors_json()  # Add errors to JSON dataset
    create_csv()  # Create CSV with metrics from JSON dataset
