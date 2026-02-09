import argparse
import json
import validators
import requests
requests.packages.urllib3.disable_warnings() # Disable SSL warnings
import os
from shared_const import *

class ModelConnection:

    def ollama(url,model,prompt):
        return requests.post(url=url,json={ "model": model, "prompt": prompt, "stream": False},verify=False)

parser = argparse.ArgumentParser(description="Select model for evaluation")
parser.add_argument("--model", required=True, help="Model to use for evaluation "+"("+ ", ".join([m.name for m in Model]) +")")
parser.add_argument("--ollama_url", default="http://localhost:11434/api/generate", help="Ollama API URL")
args = parser.parse_args()

if args.model not in [m.name for m in Model]:
    raise ValueError("Invalid model selected. Choose from "+ ", ".join([m.name for m in Model]) + ".")

if not validators.url(args.ollama_url):
    raise ValueError("Invalid URL provided for Ollama API. Please provide a valid URL.")

for s in Scenario:
    ollama_url=args.ollama_url
    model=Model[args.model].value

    print(f"Running queries for scenario {s.name} with model {model} at {ollama_url}...")

    prompts_obj=[]

    with open("./scenarios/"+s.name.lower()+"/prompts/prompts_"+s.name.lower()+".jsonl") as f:
        for line in f:
            prompts_obj.append(json.loads(line))

    
    if os.path.exists("./scenarios/"+s.name.lower()+"/results/results_"+s.name.lower()+"_"+args.model+".jsonl"):
        os.remove("./scenarios/"+s.name.lower()+"/results/results_"+s.name.lower()+"_"+args.model+".jsonl")
    else:
        print("The file does not exist")

   
    for prompt_idx, prompt in enumerate(prompts_obj):
        with open("./scenarios/"+s.name.lower()+"/results/results_"+s.name.lower()+"_"+args.model+".jsonl","a") as f:
            
            response_flag=False
            response_m_flag=True
            response_n_flag=True
            response_malformed_flag=True
            response_duplicate_flag=True
            retry_count=0
            res_obj={}

            while response_flag==False and retry_count<MAX_RETRIES:

                response_m_flag=True
                response_n_flag=True
                response_malformed_flag=True
                response_duplicate_flag=True

                try:
                    res=ModelConnection.ollama(ollama_url,model,prompt["prompt"])

                    model_response_raw=res.json()
                    model_response=model_response_raw["response"].replace('\n', '').replace('\r', '').replace('\'', '"')

                    opening_bracket_index = model_response.find('{')
                    closing_bracket_index = model_response.find('}')

                    model_response = model_response[opening_bracket_index:closing_bracket_index+1]

                    print(f"Prompt {prompt_idx+1}/{len(prompts_obj)}")
                    print(model_response)
                    response_m_flag=len(json.loads(model_response)["res_probes"])==prompt["metadata"]["m"]

                    for probe in json.loads(model_response)["res_probes"]:
                        if probe not in [x["name"] for x in prompt["metadata"]["n_probes"]]:
                            response_n_flag=False
                            break

                    if len(json.loads(model_response)["res_probes"]) != len(set(json.loads(model_response)["res_probes"])):
                        response_duplicate_flag=False
                    
                    res_obj={
                        "metadata":{
                            "scenario": prompt["metadata"]["scenario"],
                            "example": {
                                "name":prompt["metadata"]["example"]["name"],
                                "prompt":prompt["metadata"]["example"]["prompt"],
                                "probes":prompt["metadata"]["example"]["probes"],
                                "answer":prompt["metadata"]["example"]["answer"],
                                "answer_probes":prompt["metadata"]["example"]["answer_probes"]
                            },
                            "n": prompt["metadata"]["n"],
                            "m": prompt["metadata"]["m"],
                            "repetition": prompt["metadata"]["repetition"],
                            "retries": retry_count,
                            "total_duration": model_response_raw["total_duration"],
                            "load_duration": model_response_raw["load_duration"],
                            "prompt_eval_duration": model_response_raw["prompt_eval_duration"],
                            "eval_duration": model_response_raw["eval_duration"],
                            "prompt": prompt["prompt"],
                            "model": model,
                        },
                        "response": model_response
                    }
                except (json.JSONDecodeError, KeyError, IndexError):
                    response_malformed_flag=False
                response_flag=response_m_flag and response_n_flag and response_malformed_flag and response_duplicate_flag
                retry_count+=1
                if not response_m_flag:
                    print(f"Response not matching expected m={prompt['metadata']['m']}. Retrying... ({retry_count}/{MAX_RETRIES})")
                if not response_n_flag:
                    print(f"Response not matching expected probes. Retrying... ({retry_count}/{MAX_RETRIES})")
                if not response_malformed_flag:
                    print(f"Malformed response received. Retrying... ({retry_count}/{MAX_RETRIES})")
                if not response_duplicate_flag:
                    print(f"Response contains duplicate probes. Retrying... ({retry_count}/{MAX_RETRIES})")
            
            if retry_count==MAX_RETRIES:
                print(f"Max retries reached. Exiting...")
                exit(1)
            
            f.write(json.dumps(res_obj)+"\n")