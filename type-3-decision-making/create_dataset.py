import json
import random
from shared_const import *

for s in Scenario:
    print(f"Generating dataset for scenario {s.name}...")
    all_probes = []

    with open("./scenarios/"+s.name.lower()+"/"+s.name.lower()+".jsonl") as f:
        for line in f:
            all_probes.append(json.loads(line))
    
    prompt_objs = []

    for n in N:
        for m in M:
            # Only generate prompts if the number of probes (n) is greater than the number of selected probes (m)
            if m.value<n.value:

                examples = []

                with open("./examples/ml.json") as f:
                    examples = json.load(f)

                for e in examples:

                    query_probes=""

                    for x_idx,x in enumerate(e["query_probes"]):
                        if x_idx != len(e["query_probes"])-1:
                            query_probes += x["name"]+":"+x["description"]+"\n"
                        else:
                            query_probes += x["name"]+":"+x["description"]

                    answer_probes=""

                    for x_idx,x in enumerate(e["answer_probes"]):
                        if x_idx != len(e["answer_probes"])-1:
                            answer_probes += x["name"]+":"+x["description"]+"\n"
                        else:
                            answer_probes += x["name"]+":"+x["description"]
                    
                    for r in range(REPETITIONS):

                        n_probes = all_probes[0:n.value]

                        # shuffling the probes to ensure randomness
                        random.shuffle(n_probes)

                        n_probes_str=""

                        for x_idx,x in enumerate(n_probes):
                            if x_idx != len(n_probes)-1:
                                n_probes_str += x["name"]+":"+x["description"]+"\n"
                            else:
                                n_probes_str += x["name"]+":"+x["description"]

                        prompt_obj={
                            "metadata":{
                                "scenario": s.name,
                                "example": {
                                    "name":e["name"],
                                    "prompt":e["query"],
                                    "probes": e["query_probes"],
                                    "answer": e["answer"],
                                    "answer_probes": e["answer_probes"]
                                },
                                "n":n.value,
                                "m":m.value,
                                "repetition": r+1,
                                "n_probes": n_probes
                            },
                            "prompt": "Select the "+str(m.value)+" most relevant probes for the scenario "+s.name+" out of the following "+str(n.value)+" probes:\n"+n_probes_str+"\nRespond on the basis of the following example:\nQuery: '"+e["query"]+"\n"+query_probes+"'\nAnswer: '"+e["answer"]+"\n"+answer_probes+"'\nReply only with a JSON object, put the resulting probe names in a field named 'res_probes'. Do not include the description field. Do not add anything other than the JSON object. Ensure that the order in which the probes are presented does not affect your judgment." if e["name"] != "No example" else "Select the "+str(m.value)+" most relevant probes for the scenario "+s.name+" out of the following "+str(n.value)+" probes:\n"+n_probes_str+"\nReply only with a JSON object, put the resulting probe names in a field named 'res_probes'. Do not include the description field. Do not add anything other than the JSON object. Ensure that the order in which the probes are presented does not affect your judgment."
                        }
                        prompt_objs.append(prompt_obj)
            
    with open("./scenarios/"+s.name.lower()+"/prompts/prompts_"+s.name.lower()+".jsonl","w") as f:
        for i in range(len(prompt_objs)):
            f.write(json.dumps(prompt_objs[i])+"\n")
