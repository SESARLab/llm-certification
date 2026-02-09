import json
import os
import textstat
from settings import *

out_folder_path = "./out"
extradata_folder_path = "./extradata"
analyzed_folder_path = "./analyzed"
prompt_folder_path = "./prompts"

extradata_files = [f for f in os.listdir(extradata_folder_path) if os.path.isfile(os.path.join(extradata_folder_path, f))]

for extradata_f in extradata_files:

    extradata_f_name=extradata_f.split(".json")[0]

    print("Analyzing extradata "+extradata_f_name)

    prompt_files = [f for f in os.listdir(prompt_folder_path) if os.path.isfile(os.path.join(prompt_folder_path, f))]

    for pf in prompt_files:

        files = []

        pf_name=pf.split(".json")[0]

        if os.path.exists(out_folder_path+"/"+extradata_f_name+"/"+pf_name)==False:
            print(f"No output folder found for extradata file: {extradata_f_name}, skipping...")
        else:
            files = [f for f in os.listdir(out_folder_path+"/"+extradata_f_name+"/"+pf_name) if os.path.isfile(os.path.join(out_folder_path+"/"+extradata_f_name+"/"+pf_name, f))]

        final_res_total={
            "fklg":{
                "passed":0,
                "failed":0
            },
            "dale_chall":{
                "passed":0,
                "failed":0
            },
            "passed":0,
            "failed":0
        }

        os.makedirs(analyzed_folder_path, exist_ok=True)
        os.makedirs(analyzed_folder_path+"/"+extradata_f_name, exist_ok=True)
        os.makedirs(analyzed_folder_path+"/"+extradata_f_name+"/"+pf_name, exist_ok=True)

        for i in range(len(files)-1):  # excluding generation_report.json
            with open(out_folder_path+"/"+extradata_f_name+"/"+pf_name+"/out"+str(i+1)+".txt","r") as f:
                out=f.read()
                fklg_out=textstat.flesch_kincaid_grade(out)
                dale_chall=textstat.dale_chall_readability_score(out)

                final_res={
                    "fklg":{
                        "value":0.0,
                        "passed":True
                    },
                    "dale_chall":{
                        "value":0.0,
                        "passed":True
                    },
                    "passed":True
                }

                with open(analyzed_folder_path+"/"+extradata_f_name+"/"+pf_name+"/analyzed"+str(i+1)+".json","w") as f_res:
                    final_res["fklg"]["value"]=fklg_out
                    final_res["dale_chall"]["value"]=dale_chall

                    if fklg_out <= FKLG_THRESHOLD:
                        final_res["fklg"]["passed"]=True
                        final_res_total["fklg"]["passed"]+=1
                    else:
                        final_res["fklg"]["passed"]=False
                        final_res_total["fklg"]["failed"]+=1

                    final_res_total["fklg"]["avg"]=final_res_total["fklg"]["avg"]+fklg_out/REPETITIONS if "avg" in final_res_total["fklg"] else fklg_out/REPETITIONS

                    if dale_chall < DALE_CHALL_THRESHOLD:
                        final_res["dale_chall"]["passed"]=True
                        final_res_total["dale_chall"]["passed"]+=1
                    else:
                        final_res["dale_chall"]["passed"]=False
                        final_res_total["dale_chall"]["failed"]+=1
                    
                    if fklg_out <= FKLG_THRESHOLD and dale_chall < DALE_CHALL_THRESHOLD:
                        final_res["passed"]=True
                        final_res_total["passed"]=final_res_total["passed"]+1
                    else:
                        final_res["passed"]=False
                        final_res_total["failed"]=final_res_total["failed"]+1

                    final_res_total["dale_chall"]["avg"]=final_res_total["dale_chall"]["avg"]+dale_chall/REPETITIONS if "avg" in final_res_total["dale_chall"] else dale_chall/REPETITIONS

                    f_res.write(json.dumps(final_res, indent=4))

        with open(analyzed_folder_path+"/"+extradata_f_name+"/"+pf_name+"/summary.json","w") as f_final:
            f_final.write(json.dumps(final_res_total, indent=4))

        print("Final results for extradata "+extradata_f_name+" and prompt "+pf_name+":")
        print(json.dumps(final_res_total, indent=4))