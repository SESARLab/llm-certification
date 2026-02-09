import argparse
import json
import os
from shared_const import *

parser = argparse.ArgumentParser(description="Select model for evaluation")
parser.add_argument("--model", required=True, help="Model to use for evaluation "+"("+ ", ".join([m.name for m in Model]) +")")
args = parser.parse_args()

if args.model not in [m.name for m in Model]:
    raise ValueError("Invalid model selected. Choose from "+ ", ".join([m.name for m in Model]) + ".")

for s in Scenario:

    results_obj = []

    with open("./scenarios/"+s.name.lower()+"/results/results_"+s.name.lower()+"_"+args.model+".jsonl") as f:
        for line in f:
            results_obj.append(json.loads(line))
    
    evaluation_batch = []
    rep=1

    final_result_objs = []

    for res in results_obj:
        if rep==1:
            assert res["metadata"]["repetition"] == 1, "Repetition must be 1 for the first batch object"
            evaluation_batch.append(res)
            rep+=1
        elif rep==2:
            assert res["metadata"]["repetition"] == 2, "Repetition must be 2 for the second batch object"
            evaluation_batch.append(res)

            first_res_raw = evaluation_batch[0]
            first_res = json.loads(evaluation_batch[0]["response"])
            second_res_raw = evaluation_batch[1]
            second_res = json.loads(evaluation_batch[1]["response"])

            intersection_count = 0

            for probe in first_res["res_probes"]:
                if probe in second_res["res_probes"]:
                    intersection_count += 1
            
            final_result=intersection_count/res["metadata"]["m"]

            final_result_obj={
                "metadata": {
                    "scenario": res["metadata"]["scenario"],
                    "example": {
                        "name":res["metadata"]["example"]["name"],
                        "prompt":res["metadata"]["example"]["prompt"],
                        "probes":res["metadata"]["example"]["probes"],
                        "answer":res["metadata"]["example"]["answer"],
                        "answer_probes":res["metadata"]["example"]["answer_probes"]
                    },
                    "n": res["metadata"]["n"],
                    "m": res["metadata"]["m"],
                    "repetition": REPETITIONS,
                    "rep_1":{
                        "retries": first_res_raw["metadata"]["retries"],
                        "total_duration": first_res_raw["metadata"]["total_duration"],
                        "load_duration": first_res_raw["metadata"]["load_duration"],
                        "prompt_eval_duration": first_res_raw["metadata"]["prompt_eval_duration"],
                        "eval_duration": first_res_raw["metadata"]["eval_duration"],
                        "prompt": first_res_raw["metadata"]["prompt"],
                    },
                    "rep_2":{
                        "retries": second_res_raw["metadata"]["retries"],
                        "total_duration": second_res_raw["metadata"]["total_duration"],
                        "load_duration": second_res_raw["metadata"]["load_duration"],
                        "prompt_eval_duration": second_res_raw["metadata"]["prompt_eval_duration"],
                        "eval_duration": second_res_raw["metadata"]["eval_duration"],
                        "prompt": second_res_raw["metadata"]["prompt"],
                    },
                    "model":args.model
                },
                "result": round(final_result, 2)
            }

            final_result_objs.append(final_result_obj)

            evaluation_batch=[]
            rep=1
    
    with open("./scenarios/"+s.name.lower()+"/final_results/final_results_"+s.name.lower()+"_"+args.model+".jsonl", "w") as f:
        for final_res in final_result_objs:
            f.write(json.dumps(final_res) + "\n")