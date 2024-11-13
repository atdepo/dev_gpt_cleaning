import json

if __name__ == "__main__":
    with open("datasets/dataset.json", "r") as f:
        dataset = json.load(f)
        prompts = 0
        conversations = 0
        for source in dataset:
            for elem in source:
                if elem.get("ChatgptSharing") is not None:
                    for block in elem.get("ChatgptSharing"):
                        if block.get("Conversations") is not None:
                            conversations += 1
                            for conv in block["Conversations"]:
                                prompts +=1
        print(prompts)
        print(conversations)
