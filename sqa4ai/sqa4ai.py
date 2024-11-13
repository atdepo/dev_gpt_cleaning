import json
import csv
from collections import Counter
from sonarqube import SonarQubeClient
import requests


def json_read():
    page_idx = 1
    page_len = 500

    results = []
    while True:
        response = requests.get(url='http://localhost:9000/api/measures/component_tree', auth=("admin", "Mememaster1!"),
                                verify=False,
                                params={"metricKeys": "cognitive_complexity,complexity", "component": "paper-quality-final", "p": page_idx,
                                        "ps": page_len})

        content = json.loads(response.text)

        for element in content['components']:
            if element["qualifier"] == "FIL" and element["language"] == "py":
                results.append(element)
        if len(content['components']) == page_len:
            page_idx += 1
        else:
            break
    with open("sq_results.json", "w") as outfile:
        json.dump(results, outfile)


def data_retrival():
    with open('cognitive_cyclomatic.csv', mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=';')

        patterns = {
            "Zero-shot;Not Chain of Thought;Not Personas Pattern": "ZS",
            "Zero-shot;Chain of Thought;Not Personas Pattern": "ZS-CoT",
            "Zero-shot;Not Chain of Thought;Personas Pattern": "ZS-Per",
            "Zero-shot;Chain of Thought;Personas Pattern": "ZS-CoT-Per",
            "Few-shot;Not Chain of Thought;Not Personas Pattern": "FS",
            "Few-shot;Chain of Thought;Not Personas Pattern": "FS-CoT",
            "Few-shot;Not Chain of Thought;Personas Pattern": "FS-Per",
            "Few-shot;Chain of Thought;Personas Pattern": "FS-CoT-Per"
        }

        # Write header row (optional)
        csv_writer.writerow(["SNIPPET_ID", "PROMPT_PATTERN", "COGNITIVE_COMPLEXITY", "CYCLOMATIC_COMPLEXITY"])
        with open("../dev_gpt_files/outcome_step_3.json", "r") as dataset:
            with open("sq_results.json", "r") as sq:
                results = json.load(sq)
                data = json.load(dataset)
                for elem in results:

                    cognitive = 0
                    cyclomatic = 0
                    for prop in elem["measures"]:
                        if prop["metric"] == "complexity":
                            cyclomatic = int(prop["value"])
                        elif prop["metric"] == "cognitive_complexity":
                            cognitive = int(prop["value"])

                    snippet_id = elem["name"].split(".py")[0].split("snippet_")[1]
                    pp = get_pp_by_snippet_id(snippet_id, data)
                    prompt_pattern = patterns.get(pp, None)
                    csv_writer.writerow(
                        [snippet_id, prompt_pattern, cognitive, cyclomatic])


def get_pp_by_snippet_id(snippet_id, data):
    for source in data:
        if source['TopicSoftwareDevelopmentAndEngineeringFlag']:
            for block in source['ChatgptSharing']:
                blk_lst = block.get('Conversations', None)
                if blk_lst is not None:
                    for conv in blk_lst:
                        for code in conv['ListOfCode']:
                            if code['Snippet_ID'] == snippet_id:
                                return conv['Prompt_Pattern']


if __name__ == "__main__":
    #json_read()
    data_retrival()
