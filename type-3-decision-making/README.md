## Overview

This repository contains the source code, input dataset, intermediate results and detailed results of our order bias experimental evaluation.

## Evaluation Process

The evaluation is divided in the following phases:

- generation of dataset
- submission to the LLMs
- bias computation
- result analysis (quality and performance).

Note: each phase involves several commands, from executing the actual experiment to post-processing. We created one script for each phase. Each all-in-one-script assumes that

- the needed dependencies are installed
- the required parameters are provided

**Note**: input/output directories and files are hardcoded.

### Environment Setup

Our experiments were executed on a Dell laptop 7590 equipped with a CPU Intel Core i7-9750H with 6 cores @ 4.5Ghz, 16 GBs RAM, 1 TB M.2 SSD, running RHEL 10.0 and Python v3.12.9. The LLMs were hosted and queried via the [OLLAMA](https://ollama.com) REST APIs (Ollama 0.7.1), running on Kubernetes K3S 1.32.4+k3s1. The server is equipped with 2X CPU AMD EPYC 7453 28-Core (56) @ 3.49 GHz, 256 GBs RAM, 3 GPUs Nvidia L40S, 1 GPU Nvidia A40, and 1 TB M.2 SSD.

We provided a `conda` [`environment.yml`](environment.yml) file for reproducibility, though the only required dependencies is `pandas`.

**Note**: the LLMs are queried via OLLAMA, which must be installed and configured separately.

### Execution: Dataset Generation

The dataset of prompts takes as input the set of probes and examples generated offline. For this first task, we used GPT4, using the prompt in [`scenarios/cloud/prompts/prompts_cloud.jsonl`](scenarios/cloud/prompts/prompts_cloud.jsonl).

The dataset of prompts is then generated using the script [`create_dataset.py`](create_dataset.py).

### Execution: Submission to LLM

To submit the generated dataset to the selected LLM we execute the all-in-one script [`run_evaluate_model.sh`](run_evaluate_model.sh).

The script needs two additional input parameters:

- `model`: the model to which we want to submit the dataset
- `ollama_url`: an OLLAMA URL which host the selected model

### Execution: Model Evaluation

To evaluate the results obtained by the LLM we execute the all-in-one script [`evaluate_model.py`](evaluate_model.py).

The script needs an additional input parameters:

- `model`: the model whose results we want to analyze

### Execution: Result Analysis

To further analyze the results obtained by the previous stage we execute two all-in-one scripts:

- `analyze_results_quality.py`: analyze the results in terms of quality
- `analyze_results_time.py`: analyze the results in terms of performance

The scripts needs two additional input parameters:

- `model`: the model whose results we want to analyze
- `store-nan` (optional): if enabled explicitly store 'nan' in the results (recommended for plotting)

## Included Results and Settings

The directory is organized as follows:

- [`examples`](examples): contains the examples to provide to the LLMs
- [`scenarios`](scenarios): contains the scenario we want to evaluate, in terms
  - [`scenarios/X`](scenarios/X): contains one specific scenario instance files:
    - [`scenarios/X/analyzed_results_quality`](scenarios/X/analyzed_results_quality): contains the scenario quality results
    - [`scenarios/X/analyzed_results_time`](scenarios/X/analyzed_results_time): contains the scenario performance results
    - [`scenarios/X/final_results`](scenarios/X/final_results): contains the scenario evaluated results
    - [`scenarios/X/prompts`](scenarios/X/prompts): contains the scenario generated input dataset
    - [`scenarios/X/results`](scenarios/X/results): contains the scenario raw results
    - [`scenarios/X/X.jsonl`](scenarios/X/X.jsonl): contains the scenario probe dataset
  - [`scenarios/generate_dataset_prompt.json`](scenarios/generate_dataset_prompt.json): contains the prompt used to generate the initial probe list

### Main Results

**Note**: the following applies to [`scenarios/X/results`](scenarios/X/results).

We retrieve the following results for each model:

- `metadata`: set of metadata attributes:
  - `metadata/scenario`: scenario used in the specific evaluation
  - `metadata/example`: example used in the specific evaluation:
    - `metadata/example/name`: name of the example used in the specific evaluation
    - `metadata/example/prompt`: prompt provided to the model related to the example used in the specific evaluation
    - `metadata/example/probes`: probes provided to the model related to the example used in the specific evaluation
    - `metadata/example/answer`: answer provided to the model related to the example used in the specific evaluation
    - `metadata/example/answer_probes`: list of probes provided to the LLM, related to the example used in the specific evaluation
  - `metadata/n`: value of N used in the evaluation
  - `metadata/m`: value of M used in the evaluation
  - `metadata/repetitions`: current repetition number
  - `metadata/retries`: value of retries needed to obtain a valid response
  - `metadata/total_duration`: time taken to generate the response (see Ollama Docs)
  - `metadata/load_duration`: time taken to load the model (see Ollama Docs)
  - `metadata/prompt_eval_duration`: time taken to evaluate the prompt (see Ollama Docs)
  - `metadata/eval_duration`: time taken to the model to evaluate (see Ollama Docs)
  - `metadata/prompt`: prompt provided to the model
  - `metadata/model`: model used in the evaluation
- `response`: model response

### Post-Processed Results

**Note**: the following applies to [`scenarios/X/final_results`](scenarios/X/final_results).

Post-processed results performs additional evaluation on the main results. We evaluate the following results for each model:

- `metadata`: set of metadata attributes:
  - `metadata/scenario`: scenario used in the specific evaluation
  - `metadata/example`: example used in the specific evaluation:
    - `metadata/example/name`: name of the example used in the specific evaluation
    - `metadata/example/prompt`: prompt provided to the model related to the example used in the specific evaluation
    - `metadata/example/probes`: probes provided to the model related to the example used in the specific evaluation
    - `metadata/example/answer`: answer provided to the model related to the example used in the specific evaluation
    - `metadata/example/answer_probes`: answer probes provided to the model related to the example used in the specific evaluation
  - `metadata/n`: value of N used in the evaluation
  - `metadata/m`: value of M used in the evaluation
  - `metadata/repetitions`: total number of repetitions
  - `metadata/rep_X`: results obtained from repetion X:
    - `metadata/rep_X/retries`: value of retries needed to obtain a valid response
    - `metadata/rep_X/total_duration`: time taken to generated the response (see Ollama Docs)
    - `metadata/rep_X/load_duration`: time taken to load the model (see Ollama Docs)
    - `metadata/rep_X/prompt_eval_duration`: time taken to evaluate the prompt (see Ollama Docs)
    - `metadata/rep_X/eval_duration`: time taken to the model to evaluate (see Ollama Docs)
    - `metadata/rep_X/prompt`: prompt provided to the model
  - `metadata/model`: model used in the evaluation
- `result`: result obtained from the evaluation

### Analyzed Results

**Note**: the following applies to [`scenarios/X/analyzed_results_quality`](scenarios/X/analyzed_results_quality).

Results are then further analyzed to perform additional evaluation on the post-processed results in terms of quality. The analyzed results are presented in form of two CSV files.

In one file we analyze the variation of the value of N related to the value of M and the examples:

- each row corresponds a value of N
- each row shows the results varying M and examples

In the second file we analyze the variation of the value of M related to the value of N and the examples:

- each row corresponds a value of M
- each row shows the results varying N and examples

**Note**: the following applies to [`scenarios/X/analyzed_results_time`](scenarios/X/analyzed_results_time).

Results are then further analyzed to perform additional evaluation on the post-processed results in terms of performance. The analyzed results are presented in form of two CSV files per aggregation type:

- sum: sum of times taken to generate the response
- average: average of times taken to generate the response

In one file we analyze the variation of the value of N related to the value of M and the examples:

- each row corresponds a value of N
- each row shows the results varying M and examples

In the second file we analyze the variation of the value of M related to the value of N and the examples:

- each row corresponds a value of M
- each row shows the results varying N and examples

#### Configurations

An actual experiment configuration is defined in the file `shared_const.py`, there it is possible to add models and change the evaluation settings:

- scenarios: number and names
- N: total probe number
- M: probes to be selected
- models: name and corresponding versions
- repetitions: number of repetitions needed to evaluate the bias (change to this value need further modify the evaluation scripts)
- max retries: number of max retry attempts if the model output is malformed

## Code

The code directory includes the following modules:

- [`analyze_results_quality.py`](analyze_results_quality.py): script to analyze the quality results
- [`analyze_results_time.py`](analyze_results_time.py): script to analyze the performance results
- [`compare_models.sh`](compare_models.sh): script to execute the entire evaluation all at once
- [`create_dataset.py`](create_dataset.py): script to generate the input dataset
- [`environment.yml`](environment.yml): configuration file to generate a CONDA environment
- [`evaluate_model.py`](evaluate_model.py): script to evaluate the model results
- [`run_evaluate_model.sh`](run_evaluate_model.sh): script to execute the entire evaluation of a single model
- [`sep_quality.sh`](sep_quality.sh): script to execute only the quality analysis phase of all models
- [`sep_time.sh`](sep_time.sh): script to execute only the performance analysis phase of all models
- [`shared_const.py`](shared_const.py): configuration file to store the shared scripts configuration
- [`submit_to_model.py`](submit_to_model.py): script to submit the input dataset to one model

## Acknowledgments

This work was supported by:

- TII under Grant 8434000394
- MUSA -- Multilayered Urban Sustainability Action -- project, funded by the European Union -- NextGenerationEU, under the National Recovery and Resilience Plan (NRRP) Mission 4 Component 2 Investment Line 1.5: Strengthening of research structures and creation of R&D innovation ecosystems, set up of territorial leaders in R&D (CUP  G43C22001370007, Code ECS00000037)
- Project SERICS (PE00000014) under the NRRP MUR program funded by the EU -- NextGenerationEU.
- Computational resources provided by INDACO Core facility, which is a project of High Performance Computing at the University of MILAN.

Views and opinions expressed are however those of the authors only and do not necessarily reflect those of the European Union or the Italian MUR. Neither the European Union nor the Italian MUR can be held responsible for them.

## License

This work is licensed under a
[Creative Commons Attribution 4.0 International License][cc-by].

[![CC BY 4.0][cc-by-image]][cc-by]

[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-image]: https://i.creativecommons.org/l/by/4.0/88x31.png
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg