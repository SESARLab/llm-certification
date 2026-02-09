# LLM Text Resoning Metrics Experiments

The purpose of these experiments is to provide concrete validation of some LLM-generated text explanations through different metrics like FKLG and Dale-Chall.

## Project layout

A concise overview of the important files and directories:

- `prompts/` — Prompt templates and files used to drive the evaluation.
- `out/` — Raw generated text explanations (txt files).
- `analyzed/` — Evaluation outputs: per-text metrics and a summary JSON.
- `extradata/` — Ouputs for which we require an explanation to the model
- `.gitignore` — Ignore rules for local/build artifacts and sensitive files.
- `analyze.py` — Main evaluation driver: runs the pipeline and computes metrics.
- `submit_to_model.py` — Produces text explanations from prompts/models.
- `make_csv.py` — Converts evaluation results and metrics into CSV for analysis.
- `README.md` — High-level project overview, usage examples, and notes.
- `requirements.txt` — Python package dependencies required to run the tools.
- `settings.py` — Configuration values and constants shared across scripts.


## Run the experiments

1. Install dependencies
    - pip install -r requirements.txt

2. Make sure an Ollama instance (or compatible API) is running and reachable. Example URL:
    - http://localhost:11434

3. Generate artifacts (Kubernetes YAML) using the Ollama URL:
    - python3 submit_to_model.py --ollama-url http://localhost:11434

    This writes generated YAML files to the `out/` directory.

4. Run the evaluation pipeline:
    - python3 analyze.py

    Results and per-text metrics are written to `analyzed/<prompt>/` and a summary JSON is produced for each prompt.

5. Create CSV summary:
    - python3 make_csv.py

    CSV results are written to `analyzed/summary.csv` and `analyzed/detailed_summary.csv`.

Notes: to change the model queried modify the field MODEL in `settings.py`, note that the model must be installed on the Ollama instance first.