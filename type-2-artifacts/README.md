# LLM Artifacts Validation Experiments

The purpose of these experiments is to provide concrete validation of some LLM-generated artifacts through rigorous hypergraph matching.
The evaluation corresponding hypergraph is defined in the fine `graph.py`.

## Project layout

A concise overview of the important files and directories:

- `prompts/` — Prompt templates and files used to drive the evaluation.
- `out/` — Raw generated artifacts (Kubernetes YAML files).
- `eval_out/` — Evaluation outputs: per-artifact metrics and a summary JSON.
- `.gitignore` — Ignore rules for local/build artifacts and sensitive files.
- `evaluate.py` — Main evaluation driver: runs the pipeline and computes metrics.
- `generate_artifacts.py` — Produces artifacts (Kubernetes YAML) from prompts/models.
- `graph.py` — Defines the evaluation hypergraph used for matching and scoring.
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
    - python3 generate_artifacts.py --ollama-url http://localhost:11434

    This writes generated YAML files to the `out/` directory.

4. Run the evaluation pipeline:
    - python3 evaluate.py

    Results and per-artifact metrics are written to `eval_out/<prompt>/` and a summary JSON is produced for each prompt.

5. Create CSV summary:
    - python3 make_csv.py

    CSV results are written to `eval_out/summary.csv`.

Notes: to change the model queried modify the field MODEL in `settings.py`, note that the model must be installed on the Ollama instance first.