# Replication Package for **"Unveiling the Relationship Between Prompt Patterns and Quality of LLM-Generated Source Code"**

Welcome! This replication package provides all the scripts and datasets required to replicate the findings of our paper titled **"Unveiling the Relationship Between Prompt Patterns and Quality of LLM-Generated Source Code"**. Below, you'll find a detailed guide on the purpose of each script and the step-by-step process to reproduce our experiments.

## Overview of Files
The following Python scripts are included in this package, each serving a specific role in the replication process:

- **`dataset_aggregator.py`**: Prepares the dataset by removing unnecessary attributes, eliminating duplicates, and merging files into a unified dataset.
- **`topic_classification.py`**: Interacts with the LLM to classify dataset topics and generate the final version of the dataset.
- **`zero_few_shot_classification.py`**: Conducts Zero/Few-shot classification on the dataset. It produces an annotated version and saves intermediate results.
- **`chain_of_thought_classification.py`**: Performs "Chain of Thought" classification on the conversations in the dataset, providing annotations and intermediate results.
- **`personas_classification.py`**: Classifies the dataset based on "Personas" prompts and saves all annotated results.
- **`code_file_creator.py`**: Generates the source code files used for analysis in Research Question 2 (RQ2).
- **`final_step_analysis.py`**: Enhances the dataset with SonarQube metrics collected during code analysis.
- **`prompt_evaluation_platform.html`**: The platform used to help the experts analyze the conversations.
- **`statistical_analysis.jasp`**: The JASP file containing the instructions for the static analysis
- **`prompts.json`**: A file to provide easy access to all the prompts used in the work.

## How to Reproduce the Experiment
### Prerequisites
To replicate our findings, you will need:

1. **OpenAI Account**: An OpenAI account with sufficient credit. To reproduce our results using GPT-4o-mini, the expected cost is approximately $15-20. Alternatively, you could use a self-hosted LLM, but note that code modifications will be required to accommodate API differences.

2. **SonarQube**: Install a SonarQube instance for code quality analysis. We used the SonarQube Community Edition Docker Image. Ensure your instance has access to the SonarQube Web API, as this is crucial for retrieving results.

3. **JASP**: The tool used to perform the statistic analysis. It can be downloaded at https://jasp-stats.org/download/

4. **Libraries**: To install the required libraries, run the command:
```bash
     pip install openai
     pip install python-dotenv
     pip install python-sonarqube-api
```
    
### Step-by-Step Process
1. **Configuration**:
   - Fill in the `.env` file with the required credentials: OpenAI API key and SonarQube credentials.

2. **Dataset Aggregation**:
   - Run `dataset_aggregator.py` to preprocess the dataset (removes duplicates and combines files).

3. **Topic Classification**:
   - Run `topic_classification.py` to classify dataset topics and remove conversations that are out of scope.

4. **Zero/Few-shot Classification**:
   - Execute `zero_few_shot_classification.py` to classify whether user prompts contain Zero or Few-shot patterns.

5. **Chain of Thought Classification**:
   - Run `chain_of_thought_classification.py` to determine whether the user prompts follow the "Chain of Thought" prompt pattern.

6. **Personas Classification**:
   - Run `personas_classification.py` to classify whether the user prompts involve "Personas" prompt patterns.

7. **Code File Creation**:
   - Execute `code_file_creator.py` to generate the source code files that will be analyzed by SonarQube.

8. **SonarQube Analysis**:
   - Create a project on your SonarQube instance and retrieve the analysis key.
   - Run the following command to analyze the code:
     ```bash
     docker run \
       --network=bridge \
       -v "path/to/files/directory:/usr/src" sonarsource/sonar-scanner-cli \
       -Dsonar.projectKey=paper-code-quality_3 \
       -Dsonar.sources=. \
       -Dsonar.host.url=SQ_SERVER_IP:SQ_PORT \
       -Dsonar.token=<ANALYSIS_TOKEN>
     ```

9. **Final Step Analysis**:
   - Use the dataset produced by `personas_classification.py` and run `final_step_analysis.py` to gather metrics from SonarQube and augment the dataset. This script also generates CSV files for statistical analysis.

10. **Statistical Analysis**:
    - Conduct statistical analysis using JASP to explore the relationship between prompt patterns and code quality metrics.

## Notes
- Be mindful of potential costs associated with OpenAI usage.
- If you opt for a different LLM or code analysis tool, modifications will be necessary to accommodate these changes.

We hope this guide makes reproducing our work as straightforward as possible.