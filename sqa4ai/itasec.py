import json
import requests


def json_read():
    page_idx = 1
    page_len = 500

    results = []
    while True:
        response = requests.get(url='http://localhost:9000/api/hotspots/search', auth=("admin", "Mememaster1!"),
                                verify=False,
                                params={"projectKey": "paper-quality-final", "p": page_idx,
                                        "ps": page_len})

        content = json.loads(response.text)

        for element in content['hotspots']:
            if element["component"].split(".")[1] == "py":
                results.append(element)
        if len(content['components']) == page_len:
            page_idx += 1
        else:
            break
    with open("sq_security_results.json", "w") as outfile:
        json.dump(results, outfile)


if __name__ == "__main__":
    json_read()
