import argparse
import json
import os
import urllib3
import requests
from settings import *

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


extradata_folder_path = "./extradata"
prompt_folder_path = "./prompts"
prompt=""

files = [f for f in os.listdir(extradata_folder_path) if os.path.isfile(os.path.join(extradata_folder_path, f))]

for f in files:
    with open(os.path.join(extradata_folder_path, f), "r") as file:

        prompt_files = [f for f in os.listdir(prompt_folder_path) if os.path.isfile(os.path.join(prompt_folder_path, f))]

        for pf in prompt_files:
            with open(os.path.join(prompt_folder_path, pf), "r") as prompt_file:
                prompt = json.load(prompt_file)["prompt"]
                prompt += file.read()

                last_successful_index=0
                i=0
                error_during_generation=0

                while i < REPETITIONS:
                    try:
                        response = ModelConnection.ollama(ollama_url, MODEL, prompt)
                        response_txt=response.json()["response"]

                        if response_txt is None or response_txt == "":
                            raise ValueError("empty response")
                        
                        if "apologize" in response_txt.lower():
                            raise ValueError("unsuitable response")

                        os.makedirs("./out", exist_ok=True)
                        os.makedirs(f"./out/{f.split(".json")[0]}", exist_ok=True)
                        os.makedirs(f"./out/{f.split('.json')[0]}/{pf.split('.json')[0]}", exist_ok=True)

                        with open(f"./out/{f.split('.json')[0]}/{pf.split('.json')[0]}/out"+str(i+1)+".txt","w") as f_res:
                            f_res.write(response_txt)
                            last_successful_index=i
                            i+=1
                    except Exception as e:
                        print("Error during generation ", str(e))
                        i = last_successful_index
                        error_during_generation += 1
                
                with open(f"./out/{f.split('.json')[0]}/{pf.split('.json')[0]}/generation_report.json","w") as report_f:
                    json.dump({
                        "successful_generations": REPETITIONS,
                        "failed_generations": error_during_generation
                    }, report_f)