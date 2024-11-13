import json
import re
from sonarqube import SonarQubeClient
from collections import Counter
import csv
import os
from statistics import mean, median
# from dotenv import load_dotenv

# Mapping of file extensions to programming languages
extension_to_language = {
        'python': 'py',
        'javascript': 'js',
        'typescript': 'ts',
        #'java': 'java',
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


def retrieve():
    sonar = SonarQubeClient(sonarqube_url="http://localhost:9000", username="admin", password="Mememaster1!")
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
                                            val = {"type": el["type"], "dimension": imp["softwareQuality"],
                                                   "severity": imp["severity"]}
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

    # Open and read the log file line by line
    with open('../files/log.txt', 'r') as f:
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
                                    code["QualityMeasurement"] = [{"type": "Compilation error during analysis",
                                                                  "dimension": None, "severity": None}]

        with open('outcome_step_3.json', 'w') as f:
            json.dump(data, f, indent=4)


def get_error(data, name):
    for elem in data.values():
        for string in elem:
            if string.split(".")[0] == f"snippet_{name}":
                return True
    return False


def find_file_by_name(path, filename):
    """
    Search for a file by its name (without extension) in the given path and its subdirectories.

    :param path: Path to search in.
    :param filename: Filename without the extension.
    :return: True if the file is found, otherwise False.
    """
    for root, dirs, files in os.walk(path):
        # Check for matching files in the current directory
        for file in files:
            name, _ = os.path.splitext(file)
            if name == filename:
                return True

        # Recursively check within each directory
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if find_file_by_name(dir_path, filename):
                return True
    return False


def create_csv():

    with open('outcome_step_3.json', 'r') as file:
        data = json.load(file)
        with open('issue_counts.csv', mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=';')

            # Write header row (optional)
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


def create_csv_2():
    with open('outcome_step_3.json', 'r') as file:
        data = json.load(file)
        with open('conv_counts_v2.csv', mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=';')

            # Write header row (optional)
            csv_writer.writerow(["CONVERSATION_ID", "CONVERSATION_COUNT", "MAINTAINABILITY_MEAN", "SECURITY_MEAN", "RELIABILITY_MEAN", "MAINTAINABILITY_MEDIAN", "SECURITY_MEDIAN", "RELIABILITY_MEDIAN"])
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

                                # Determine counts of each metric
                                if qm:
                                    counter_array.append(Counter(item["dimension"] for item in qm))

                if conv_counter > 1:
                    # Extract counts for each item across all Counter objects
                    counts_main = [counter["MAINTAINABILITY"] for counter in counter_array]
                    counts_sec = [counter["SECURITY"] for counter in counter_array]
                    counts_rel = [counter["RELIABILITY"] for counter in counter_array]

                    mean_main = 0
                    mean_sec = 0
                    mean_rel = 0

                    # Calculate mean for each item
                    if len(counts_main) > 0:
                        mean_main = mean(counts_main)
                    if len(counts_sec) > 0:
                        mean_sec = mean(counts_sec)
                    if len(counts_rel) > 0:
                        mean_rel = mean(counts_rel)

                    # Calculate median for each item
                    median_main = 0
                    median_sec = 0
                    median_rel = 0
                    if len(counts_main) > 0:
                        median_main = median(counts_main)
                    if len(counts_sec) > 0:
                        median_sec = median(counts_sec)
                    if len(counts_rel) > 0:
                        median_rel = median(counts_rel)

                    # Write the data to CSV
                    csv_writer.writerow([conv_id, conv_counter, mean_main, mean_sec, mean_rel, median_main, median_sec, median_rel])
                elif len(counter_array) > 0:
                    elem = counter_array[0]
                    csv_writer.writerow(
                        [conv_id, conv_counter, elem.get("MAINTAINABILITY", 0), elem.get("SECURITY", 0), elem.get("RELIABILITY",0), elem.get("MAINTAINABILITY", 0), elem.get("SECURITY", 0), elem.get("RELIABILITY",0)])
                else:
                    csv_writer.writerow(
                        [conv_id, conv_counter, 0,0,0,0,0,0])


if __name__ == '__main__':
    # load_dotenv()
    # retrieve()
    # add_quality_metrics_json()
    # prompt_patterns_join()
    # build_json_file_errors()
    # add_errors_json()
    create_csv_2()

    # 8748: java: 369 + dati a sq:8379
    # 8379 = 755 nc + 7624 compiled
