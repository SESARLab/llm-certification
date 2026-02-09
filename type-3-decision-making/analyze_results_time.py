####
# recap of the fields returned by OLLAMA /api/generate:
# total_duration: time spent generating the response
# load_duration: time spent in nanoseconds loading the model
# prompt_eval_duration: time spent in nanoseconds evaluating the prompt
# eval_duration: time in nanoseconds spent generating the response
# For instance:
# "total_duration": 45631209095, "load_duration": 23127817, "prompt_eval_duration": 1183582545, "eval_duration": 44423144462
# In our analysis, we consider only "prompt_eval_duration" and "eval_duration".
####


import argparse
import json

import numpy as np
import pandas as pd

from shared_const import *


parser = argparse.ArgumentParser(description="Select model for evaluation")
parser.add_argument("--model", required=True, choices=[m.name for m in Model],
                    help="Model to use for evaluation "+"("+ ", ".join([m.name for m in Model]) +")")
parser.add_argument('--store-nan', action='store_true', help='If enabled explicitly store \'nan\' in the results')
args = parser.parse_args()

AVG = 'AVG'
SUM = 'SUM'

AVG_SUM = [AVG, SUM]


model = args.model

for s in Scenario:

    results_objs = []

    # load the result file.

    with open("./scenarios/"+s.name.lower()+"/final_results/final_results_"+s.name.lower()+"_"+model+".jsonl", "r") as f:
        for line in f:
            results_objs.append(json.loads(line))

    # we basically create two csv like this:
    # N exec_time_with_M=1_E=1, exec_time_with_M=1,E=2, ... including one final when we have an average
    # of all the examples given a value of M (excluding when we do not have an example
    # For instance, we have M=1, example=first, time=3;  M=1, examples=last, time=5;
    # M=1, examples=NO, time=1
    # M=2, example=first, time=13;  M=2, examples=last, time=15; M=2, examples=NO, time=1
    # -> we will have two values to report
    # M_1_E_ALL -> 3+5/2, M_2_E_ALL -> 13+15/2
    # )
    # the second file has the same structure, but the first column is M.

    # we also need to load the examples.
    with open("./examples/ml.json") as f:
        examples = json.load(f)

    final_results = {
        'AVG': {},
        'SUM': {}
    }

    for n in N:
        n_key = f"n_{n.value}"
        for m in M:
            # there are combinations of N and M that are not present in the results.
            # the value is to True only when we are there.
            # (later we need to know whether this combination)
            valid_combo = False
            # average value of the duration for this m
            over_example_avg = {AVG: 0, SUM: 0}
            over_example_counter = 0
            for e in examples:

                e_m_key = f"e_{e["name"]}_m_{m.value}"

                # add the key if not there
                if n_key not in final_results[AVG]:
                    for aggregation_type in AVG_SUM:
                        final_results[aggregation_type][n_key] = {}
                if e_m_key not in final_results[AVG][n_key]:
                    for aggregation_type in AVG_SUM:
                        final_results[aggregation_type][n_key][e_m_key] = {}

                # now, we iterate over the set of results to find the one we are interested in.
                for results_obj in results_objs:
                    if results_obj["metadata"]["n"] == n.value and results_obj["metadata"]["m"] == m.value and results_obj["metadata"]["example"]["name"] == e["name"]:
                        valid_combo = True

                        answer_1_time = results_obj['metadata']['rep_1']['prompt_eval_duration'] + \
                                        results_obj['metadata']['rep_1']["eval_duration"]
                        answer_2_time = results_obj['metadata']['rep_2']['prompt_eval_duration'] + \
                                        results_obj['metadata']['rep_2']["eval_duration"]
                        time_sum = answer_1_time + answer_2_time
                        time_avg = time_sum / 2

                        # add the time
                        final_results[AVG][n_key][e_m_key] = time_avg
                        final_results[SUM][n_key][e_m_key] = time_sum

                        # also, if it is an example, we add it
                        if e['name'] != EXAMPLE_NO_EXAMPLE:
                            over_example_avg[AVG] += time_avg
                            over_example_avg[SUM] += time_sum
                            over_example_counter += 1

                if not valid_combo:
                    # if not found, set to 0 for this key.
                    for aggregation_type in AVG_SUM:
                        final_results[aggregation_type][n_key][e_m_key] = None

            if valid_combo:
                # this is done outside because it is aggregation over the examples.
                final_results[AVG][n_key][f'e_ALL_m_{m.value}'] = over_example_avg[AVG] / over_example_counter
                final_results[SUM][n_key][f'e_ALL_m_{m.value}'] = over_example_avg[SUM] / over_example_counter

    for aggregation_type in AVG_SUM:
        final_results_df = pd.DataFrame.from_dict(final_results[aggregation_type], orient='index')
        final_results_df, export_kwargs = finalize_df(final_results_df, store_nan=args.store_nan, index_label='n')
        final_results_df.to_csv(
           f"./scenarios/{s.name.lower()}/analyzed_results_time/analyzed_results_{s.name.lower()}_{aggregation_type}_{model}_n.csv",
           **export_kwargs)



    final_results = {
        'AVG': {},
        'SUM': {}
    }

    # now, let's vary m.
    for m in M:
        m_key = f"m_{m.value}"
        for n in N:
            valid_combo = False
            over_example_avg = {AVG: 0, SUM: 0}
            over_example_counter = 0
            for e in examples:

                e_n_key = f"e_{e["name"]}_n_{n.value}"

                # add the key if not there
                if m_key not in final_results[AVG]:
                    for aggregation_type in AVG_SUM:
                        final_results[aggregation_type][m_key] = {}
                if e_n_key not in final_results[AVG][m_key]:
                    for aggregation_type in AVG_SUM:
                        final_results[aggregation_type][m_key][e_n_key] = {}

                # now, we iterate over the set of results to find the one we are interested in.
                for results_obj in results_objs:
                    if results_obj["metadata"]["n"] == n.value and results_obj["metadata"]["m"] == m.value and results_obj["metadata"]["example"]["name"] == e["name"]:
                        valid_combo = True

                        answer_1_time = results_obj['metadata']['rep_1']['prompt_eval_duration'] + \
                                        results_obj['metadata']['rep_1']["eval_duration"]
                        answer_2_time = results_obj['metadata']['rep_2']['prompt_eval_duration'] + \
                                        results_obj['metadata']['rep_2']["eval_duration"]
                        time_sum = answer_1_time + answer_2_time
                        time_avg = time_sum / 2

                        # add the time
                        final_results[AVG][m_key][e_n_key] = time_avg
                        final_results[SUM][m_key][e_n_key] = time_sum

                        # also, if it is an example, we add it
                        if e['name'] != EXAMPLE_NO_EXAMPLE:
                            over_example_avg[AVG] += time_avg
                            over_example_avg[SUM] += time_sum
                            over_example_counter += 1

                if not valid_combo:
                    # if not found, set to 0 for this key.
                    for aggregation_type in AVG_SUM:
                        final_results[aggregation_type][m_key][e_n_key] = None

            if valid_combo:
                final_results[AVG][m_key][f'e_ALL_n_{n.value}'] = over_example_avg[AVG] / over_example_counter
                final_results[SUM][m_key][f'e_ALL_n_{n.value}'] = over_example_avg[SUM] / over_example_counter

    for aggregation_type in AVG_SUM:
        final_results_df = pd.DataFrame.from_dict(final_results[aggregation_type], orient='index')
        final_results_df, export_kwargs = finalize_df(final_results_df, store_nan=args.store_nan, index_label='m')
        final_results_df.to_csv(
            f"./scenarios/{s.name.lower()}/analyzed_results_time/analyzed_results_{s.name.lower()}_{aggregation_type}_{model}_m.csv",
            **export_kwargs)