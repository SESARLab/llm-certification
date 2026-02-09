import json
import os
import urllib3
import requests
from settings import *
import argparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ModelConnection:

    def ollama(url,model,prompt):
        return requests.post(url=url,json={ "model": model, "prompt": prompt, "stream": False},verify=False)


parser = argparse.ArgumentParser()
parser.add_argument("--ollama-url", "-u", help="OLLAMA server URL", default=None)
args, _ = parser.parse_known_args()

if not args.ollama_url:
    print("OLLAMA URL not provided. Please provide it using the --ollama-url or -u argument.")
    exit(1)

ollama_url = args.ollama_url

prompt_folder_path = "./prompts"
prompt=""

files = [f for f in os.listdir(prompt_folder_path) if os.path.isfile(os.path.join(prompt_folder_path, f))]

for f in files:
    with open(os.path.join(prompt_folder_path, f), "r") as file:
        prompt = json.load(file)["prompt"]

        last_successful_index=0
        i=0
        generation_errors=0

        while i < REPETITIONS:
            try:
                response = ModelConnection.ollama(ollama_url, MODEL, prompt)
                response_yaml=response.json()["response"].split("```yaml")[1].split("```")[0].strip()

                os.makedirs("./out", exist_ok=True)
                os.makedirs(f"./out/{f.split(".json")[0]}", exist_ok=True)

                with open(f"./out/{f.split(".json")[0]}/out"+str(i+1)+".yaml","w") as f_res:
                    f_res.write(response_yaml)
                    last_successful_index=i
                    i+=1
            except Exception as e:
                print("Error during generation ", str(e))
                i = last_successful_index
                generation_errors += 1
        
        with open(f"./out/{f.split('.json')[0]}/generation_stats.json","w") as f_stats:
            json.dump({
                "successful_generations": REPETITIONS,
                "generation_errors": generation_errors
            }, f_stats)