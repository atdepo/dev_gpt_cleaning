import json
import re
from sonarqube import SonarQubeClient
#from dotenv import load_dotenv


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


def json_increment():
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
                                    i += 1

    with open('outcome_step_1.json', 'w') as f:
        json.dump(json_data, f, indent=4)


def get_snippet(data, i, j):

    snip = []
    for elem in data:
        coords = elem['component'].split("/")[1].split(".")[0].split("_")[1:3]

        if int(coords[0]) == i and int(coords[1]) == j:
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

def build_csv_analysis():

    with open('outcome_step_2.json', 'r') as f:
        data = json.load(f)
        


if __name__ == '__main__':
    # load_dotenv()
    # retrieve()
    # json_increment()
    # prompt_patterns_join()
    build_csv_analysis()
