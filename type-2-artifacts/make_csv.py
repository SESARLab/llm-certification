import json
import yaml
import os
import csv
from graph import *
from settings import *

eval_output_folder_path = "./eval_out"
prompt_folder_path = "./prompts"

prompt_files = [f for f in os.listdir(prompt_folder_path) if os.path.isfile(os.path.join(prompt_folder_path, f))]

with open(eval_output_folder_path+"/summary.csv", "w", newline='') as csv_file:
    writer = csv.writer(csv_file, delimiter=',')
    writer.writerow(["","Average Passed", "Average Root User Check", "Average Read Only FS Check", "Average Capabilities Check", "Average Evaluation Base Passed", "Average Seccomp Check Passed", "Average Seccomp Check Null"])

    for prompt_file_out in prompt_files:

        print(f"Evaluating prompt file: {prompt_file_out}")

        summary={}
        with open(eval_output_folder_path+"/"+prompt_file_out.split(".json")[0]+"/summary.json", "r") as f:
            summary = json.load(f)

        writer.writerow([prompt_file_out.split(".json")[0],summary["passed"]/REPETITIONS, summary["root_user_check"]/REPETITIONS, summary["read_only_fs_check"]/REPETITIONS, summary["capabilities_check"]/REPETITIONS, summary["evaluation_base_passed"]/REPETITIONS, summary["seccomp_check_passed"]/REPETITIONS, summary["seccomp_check_null"]/REPETITIONS])
