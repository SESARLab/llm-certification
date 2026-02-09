import argparse
import json
import os
import pandas as pd
from shared_const import *


parser = argparse.ArgumentParser(description="Select model for evaluation")
parser.add_argument("--model", required=True, choices=[m.name for m in Model],
                    help="Model to use for evaluation "+"("+ ", ".join([m.name for m in Model]) +")")
parser.add_argument('--store-nan', action='store_true', help='If enabled explicitly store \'nan\' in the results')
args = parser.parse_args()

# if args.model not in [m.name for m in Model]:
#     raise ValueError("Invalid model selected. Choose from "+ ", ".join([m.name for m in Model]) + ".")

model = args.model

for s in Scenario:

    results_objs = []

    with open("./scenarios/"+s.name.lower()+"/final_results/final_results_"+s.name.lower()+"_"+model+".jsonl", "r") as f:
        for line in f:
            results_objs.append(json.loads(line))

    # Debugging section
    # Only for debugging purposes

    medium_result=0

    for tmp_obj in results_objs:
        medium_result += float(tmp_obj["result"])
        
    medium_result /= len(results_objs)

    print(f"Average result for scenario {s.name}: {medium_result:.2f}")

    # End of debugging section
        
    final_results = {}

    for n in N:
        with open("./examples/ml.json") as f:
                examples = json.load(f)
        for e in examples:
            for m in M:
                for results_obj in results_objs:
                    n_key = f"n_{n.value}"
                    e_m_key = f"e_{e["name"]}_m_{m.value}"

                    if n_key not in final_results:
                        final_results[n_key] = {}
                    if e_m_key not in final_results[n_key]:
                        final_results[n_key][e_m_key] = None
                    if results_obj["metadata"]["n"] == n.value and results_obj["metadata"]["m"] == m.value and results_obj["metadata"]["example"]["name"] == e["name"]:
                        final_results[n_key][e_m_key]=results_obj["result"]

    final_results_df = pd.DataFrame.from_dict(final_results, orient='index')
    final_results_df, export_kwargs = finalize_df(final_results_df, store_nan=args.store_nan, index_label='n')

    print(final_results_df)

    final_results_df.to_csv(f"./scenarios/{s.name.lower()}/analyzed_results_quality/analyzed_results_{s.name.lower()}_{model}_n.csv", **export_kwargs)

    final_results = {}

    for m in M:
        with open("./examples/ml.json") as f:
                examples = json.load(f)
        for e in examples:
            for n in N:
                for results_obj in results_objs:
                    m_key = f"m_{m.value}"
                    e_n_key = f"e_{e["name"]}_n_{n.value}"

                    if m_key not in final_results:
                        final_results[m_key] = {}
                    if e_n_key not in final_results[m_key]:
                        final_results[m_key][e_n_key] = None
                    if results_obj["metadata"]["n"] == n.value and results_obj["metadata"]["m"] == m.value and results_obj["metadata"]["example"]["name"] == e["name"]:
                        final_results[m_key][e_n_key]=results_obj["result"]
        
    final_results_df = pd.DataFrame.from_dict(final_results, orient='index')
    final_results_df, export_kwargs = finalize_df(final_results_df, store_nan=args.store_nan, index_label='m')

    print(final_results_df)

    final_results_df.to_csv(f"./scenarios/{s.name.lower()}/analyzed_results_quality/analyzed_results_{s.name.lower()}_{model}_m.csv", **export_kwargs)
