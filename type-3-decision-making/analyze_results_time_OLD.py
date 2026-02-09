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
import pandas as pd
from shared_const import *


parser = argparse.ArgumentParser(description="Select model for evaluation")
parser.add_argument("--model", required=True, choices=[m.name for m in Model],
                    help="Model to use for evaluation "+"("+ ", ".join([m.name for m in Model]) +")")
args = parser.parse_args()


model = args.model

RETRY_YES = 'RETRY_Y'
RETRY_NO = 'RETRY_N'

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
        RETRY_YES: {},
        RETRY_NO: {},
    }

    for n in N:
        n_key = f"n_{n.value}"
        for m in M:
            # there are combinations of N and M that are not present in the results.
            # the value is to True only when we are there.
            # (later we need to know whether this combination)
            valid_combo = False
            # average value of the duration for this m
            time_avg_examples = {RETRY_YES: 0, RETRY_NO: 0}
            # and counter over how many times it has been added, that we use for average computation
            # we zero it for every new value of m.
            time_avg_counter = {RETRY_YES: 0, RETRY_NO: 0}
            for e in examples:
                for results_obj in results_objs:
                    e_m_key = f"e_{e["name"]}_m_{m.value}"

                    if n_key not in final_results[RETRY_YES]:
                        final_results[RETRY_NO][n_key] = {}
                        final_results[RETRY_YES][n_key] = {}
                    if e_m_key not in final_results[RETRY_YES][n_key]:
                        final_results[RETRY_NO][n_key][e_m_key] = None
                        final_results[RETRY_YES][n_key][e_m_key] = None

                    n_retry = results_obj['metadata']['repetition']

                    if results_obj["metadata"]["n"] == n.value and results_obj["metadata"]["m"] == m.value and results_obj["metadata"]["example"]["name"] == e["name"]:
                        valid_combo = True
                        # for the no-retry, we just take the last one
                        last_rep_key = f'rep_{n_retry}'
                        final_results[RETRY_NO][n_key][e_m_key] = results_obj['metadata'][last_rep_key]['prompt_eval_duration']+results_obj['metadata'][last_rep_key]["eval_duration"]
                        # for the yes-retry, we iterate.
                        exec_time = 0
                        for rep in range(n_retry,):
                            # +1 because rep starts at 1
                            rep_key = f'rep_{rep+1}'
                            exec_time += results_obj['metadata'][rep_key]['prompt_eval_duration']+results_obj['metadata'][rep_key]["eval_duration"]

                            # we also increment the counter we use for the average across all examples.
                            time_avg_counter[RETRY_YES] += 1

                        final_results[RETRY_YES][n_key][e_m_key] = exec_time

                        # now, we retrieve the values we need for the average over the examples
                        if e['name'] != EXAMPLE_NO_EXAMPLE:
                            # for the one without retry, it's fairly easy.
                            time_avg_examples[RETRY_NO] += (results_obj['metadata'][last_rep_key]['prompt_eval_duration']+results_obj['metadata'][last_rep_key]["eval_duration"])
                            # and we increment the corresponding counter
                            time_avg_counter[RETRY_NO] += 1
                            # for the one with retry, we use the value we computed above, knowing that the counter
                            # has been already incremented.
                            time_avg_examples[RETRY_YES] += exec_time

            # try:
            #    final_results[RETRY_NO][n_key][f'e_ALL_m_{m.value}'] = time_avg_examples[RETRY_NO]/time_avg_counter[RETRY_NO]
            # except ZeroDivisionError as e:
                # if there is a zero-division error, it means that the counter is never incremented, meaning
                # that we are working with an incompatible combination of values of N and M,
                # print(f'zero division error for value: {time_avg_examples[RETRY_NO]}, n: {n.value}, m: {m.value}')
                # raise e
            if valid_combo:
                final_results[RETRY_NO][n_key][f'e_ALL_m_{m.value}'] = time_avg_examples[RETRY_NO] / time_avg_counter[
                    RETRY_NO]
                final_results[RETRY_YES][n_key][f'e_ALL_m_{m.value}'] = time_avg_examples[RETRY_YES] / time_avg_counter[
                RETRY_YES]

    # and now we export the results.
    for retry_type in [RETRY_YES, RETRY_NO]:
        final_results_df = pd.DataFrame.from_dict(final_results[retry_type], orient='index')
        final_results_df.to_csv(
            f"./scenarios/{s.name.lower()}/analyzed_results_time/analyzed_results_{s.name.lower()}_{retry_type}_{model}_n.csv", index=True)

    final_results = {
        RETRY_YES: {},
        RETRY_NO: {},
    }

    # now, let's vary m.
    for m in M:
        m_key = f"m_{m.value}"
        for n in N:
            # there are combinations of N and M that are not present in the results.
            # the value is to True only when we are there.
            # (later we need to know whether this combination)
            valid_combo = False
            # average value of the duration for this m
            time_avg_examples = {RETRY_YES: 0, RETRY_NO: 0}
            # and counter over how many times it has been added, that we use for average computation
            # we zero it for every new value of m.
            time_avg_counter = {RETRY_YES: 0, RETRY_NO: 0}
            for e in examples:
                for results_obj in results_objs:
                    e_n_key = f"e_{e["name"]}_n_{n.value}"

                    if m_key not in final_results[RETRY_YES]:
                        final_results[RETRY_NO][m_key] = {}
                        final_results[RETRY_YES][m_key] = {}
                    if e_n_key not in final_results[RETRY_YES][m_key]:
                        final_results[RETRY_NO][m_key][e_n_key] = None
                        final_results[RETRY_YES][m_key][e_n_key] = None

                    n_retry = results_obj['metadata']['repetition']

                    if results_obj["metadata"]["n"] == n.value and results_obj["metadata"]["m"] == m.value and \
                            results_obj["metadata"]["example"]["name"] == e["name"]:
                        valid_combo = True
                        # for the no-retry, we just take the last one
                        last_rep_key = f'rep_{n_retry}'
                        final_results[RETRY_NO][m_key][e_n_key] = results_obj['metadata'][last_rep_key]['prompt_eval_duration'] + \
                                                                  results_obj['metadata'][last_rep_key]["eval_duration"]
                        # for the yes-retry, we iterate.
                        exec_time = 0
                        for rep in range(n_retry, ):
                            # +1 because rep starts at 1
                            rep_key = f'rep_{rep + 1}'
                            exec_time += results_obj['metadata'][rep_key]['prompt_eval_duration'] + results_obj['metadata'][rep_key][
                                "eval_duration"]

                            # we also increment the counter we use for the average across all examples.
                            time_avg_counter[RETRY_YES] += 1

                        final_results[RETRY_YES][m_key][e_n_key] = exec_time

                        # now, we retrieve the values we need for the average over the examples
                        if e['name'] != EXAMPLE_NO_EXAMPLE:
                            # for the one without retry, it's fairly easy.
                            time_avg_examples[RETRY_NO] += (
                                        results_obj['metadata'][last_rep_key]['prompt_eval_duration'] + results_obj['metadata'][last_rep_key][
                                    "eval_duration"])
                            # and we increment the corresponding counter
                            time_avg_counter[RETRY_NO] += 1
                            # for the one with retry, we use the value we computed above, knowing that the counter
                            # has been already incremented.
                            time_avg_examples[RETRY_YES] += exec_time

            if valid_combo:
                final_results[RETRY_NO][m_key][f'e_ALL_n_{n.value}'] = time_avg_examples[RETRY_NO] / time_avg_counter[
                    RETRY_NO]
                final_results[RETRY_YES][m_key][f'e_ALL_n_{n.value}'] = time_avg_examples[RETRY_YES] / time_avg_counter[
                    RETRY_YES]

    # and now we export the results.
    for retry_type in [RETRY_YES, RETRY_NO]:
        final_results_df = pd.DataFrame.from_dict(final_results[retry_type], orient='index')
        final_results_df.to_csv(
            f"./scenarios/{s.name.lower()}/analyzed_results_time/analyzed_results_{s.name.lower()}_{retry_type}_{model}_m.csv",
            index=True)
