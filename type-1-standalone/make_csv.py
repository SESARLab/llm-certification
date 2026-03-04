import json
import os
import csv
from settings import *

eval_output_folder_path = "./analyzed"
extradata_folder_path = "./extradata"
prompt_folder_path = "./prompts"

extradata_files = [f for f in os.listdir(extradata_folder_path) if os.path.isfile(os.path.join(extradata_folder_path, f))]

prompt_files = [f for f in os.listdir(prompt_folder_path) if os.path.isfile(os.path.join(prompt_folder_path, f))]

extradata_map={}
mega_summary={}

for extradata_f in extradata_files:

    extradata_f_name=extradata_f.split(".json")[0]

    for prompt_file_out in prompt_files:

        prompt_file_name=prompt_file_out.split(".json")[0]

        summary={}
        with open(eval_output_folder_path+"/"+extradata_f_name+"/"+prompt_file_name+"/summary.json", "r") as f:
            summary = json.load(f)
        
        if prompt_file_name not in mega_summary:
            mega_summary[prompt_file_name] = {
                "result":0.0,
                "result_fklg":0.0,
                "result_dale_chall":0.0,
                "result_fklg_std_dev_avg":0.0,
                "result_dale_chall_std_dev_avg":0.0
            }

        extradata_f_name_collapsed=extradata_f_name.split("-")[0]

        if extradata_f_name_collapsed not in mega_summary[prompt_file_name]:
            mega_summary[prompt_file_name][extradata_f_name_collapsed] = {
                "result":False,
                "result_fklg_correct":0.0,
                "result_fklg_correct_std_dev_avg":0.0,
                "result_fklg_incorrect":0.0,
                "result_fklg_incorrect_std_dev_avg":0.0,
                "result_dale_chall_correct":0.0,
                "result_dale_chall_correct_std_dev_avg":0.0,
                "result_dale_chall_incorrect":0.0,
                "result_dale_chall_incorrect_std_dev_avg":0.0
            }

        if prompt_file_name not in extradata_map:
            extradata_map[prompt_file_name]={}

        if extradata_f_name_collapsed not in extradata_map[prompt_file_name]:
            extradata_map[prompt_file_name][extradata_f_name_collapsed]=0

        if summary["passed"]>0:
            extradata_map[prompt_file_name][extradata_f_name_collapsed]+=1

        mega_summary[prompt_file_name][extradata_f_name_collapsed]["result"]=True if extradata_map[prompt_file_name][extradata_f_name_collapsed]==2 else False
        if extradata_f_name.split("-")[1]=="correct":
            mega_summary[prompt_file_name][extradata_f_name_collapsed]["result_fklg_correct"] = summary["fklg"]["avg"]
            mega_summary[prompt_file_name][extradata_f_name_collapsed]["result_fklg_correct_std_dev_avg"] = summary["fklg"]["std_dev_avg"]
            mega_summary[prompt_file_name][extradata_f_name_collapsed]["result_dale_chall_correct"] = summary["dale_chall"]["avg"]
            mega_summary[prompt_file_name][extradata_f_name_collapsed]["result_dale_chall_correct_std_dev_avg"] = summary["dale_chall"]["std_dev_avg"]
        if extradata_f_name.split("-")[1]=="incorrect":
            mega_summary[prompt_file_name][extradata_f_name_collapsed]["result_fklg_incorrect"] = summary["fklg"]["avg"]
            mega_summary[prompt_file_name][extradata_f_name_collapsed]["result_fklg_incorrect_std_dev_avg"] = summary["fklg"]["std_dev_avg"]
            mega_summary[prompt_file_name][extradata_f_name_collapsed]["result_dale_chall_incorrect"] = summary["dale_chall"]["avg"]
            mega_summary[prompt_file_name][extradata_f_name_collapsed]["result_dale_chall_incorrect_std_dev_avg"] = summary["dale_chall"]["std_dev_avg"]
        
        mega_summary[prompt_file_name]["result"]+=1 if mega_summary[prompt_file_name][extradata_f_name_collapsed]["result"] else 0
        # these four lines will be executed two times, the second is the right one
        mega_summary[prompt_file_name]["result_fklg"]=(mega_summary[prompt_file_name][extradata_f_name_collapsed]["result_fklg_correct"]+mega_summary[prompt_file_name][extradata_f_name_collapsed]["result_fklg_incorrect"])/2
        mega_summary[prompt_file_name]["result_dale_chall"]=(mega_summary[prompt_file_name][extradata_f_name_collapsed]["result_dale_chall_correct"]+mega_summary[prompt_file_name][extradata_f_name_collapsed]["result_dale_chall_incorrect"])/2
        mega_summary[prompt_file_name]["result_fklg_std_dev_avg"]=(mega_summary[prompt_file_name][extradata_f_name_collapsed]["result_fklg_correct_std_dev_avg"]+mega_summary[prompt_file_name][extradata_f_name_collapsed]["result_fklg_incorrect_std_dev_avg"])/2
        mega_summary[prompt_file_name]["result_dale_chall_std_dev_avg"]=(mega_summary[prompt_file_name][extradata_f_name_collapsed]["result_dale_chall_correct_std_dev_avg"]+mega_summary[prompt_file_name][extradata_f_name_collapsed]["result_dale_chall_incorrect_std_dev_avg"])/2

with open(eval_output_folder_path+"/summary.csv", "w", newline='') as csv_file:
    writer = csv.writer(csv_file, delimiter=',')
    writer.writerow(["","Result", "Result FKLG", "Result FKLG STD Dev Avg", "Result Dale Chall", "Result Dale Chall STD Dev Avg"])
    for prompt_file_name, summary in mega_summary.items():
        writer.writerow([prompt_file_name, summary["result"], summary["result_fklg"], summary["result_fklg_std_dev_avg"], summary["result_dale_chall"], summary["result_dale_chall_std_dev_avg"]])

with open(eval_output_folder_path+"/detailed_summary.csv", "w", newline='') as csv_file:
    writer = csv.writer(csv_file, delimiter=',')
    title_row=[""]
    
    for extradata_f in extradata_files:
        extradata_f_name_collapsed=extradata_f.split(".json")[0].split("-")[0]
        if extradata_f_name_collapsed+" Result" not in title_row and extradata_f_name_collapsed+" AVG FKLG Correct" not in title_row and extradata_f_name_collapsed+" AVG FKLG Correct Std Dev Avg" not in title_row and extradata_f_name_collapsed+" AVG FKLG Incorrect" not in title_row and extradata_f_name_collapsed+" AVG FKLG Incorrect Std Dev Avg" not in title_row and extradata_f_name_collapsed+" AVG Dale Chall Correct" not in title_row and extradata_f_name_collapsed+" AVG Dale Chall Correct Std Dev Avg" not in title_row and extradata_f_name_collapsed+" AVG Dale Chall Incorrect" not in title_row and extradata_f_name_collapsed+" AVG Dale Chall Incorrect Std Dev Avg" not in title_row:
            title_row.append(extradata_f_name_collapsed+" Result")
            title_row.append(extradata_f_name_collapsed+" AVG FKLG Correct")
            title_row.append(extradata_f_name_collapsed+" AVG FKLG Correct Std Dev Avg")
            title_row.append(extradata_f_name_collapsed+" AVG FKLG Incorrect")
            title_row.append(extradata_f_name_collapsed+" AVG FKLG Incorrect Std Dev Avg")
            title_row.append(extradata_f_name_collapsed+" AVG Dale Chall Correct")
            title_row.append(extradata_f_name_collapsed+" AVG Dale Chall Correct Std Dev Avg")
            title_row.append(extradata_f_name_collapsed+" AVG Dale Chall Incorrect")
            title_row.append(extradata_f_name_collapsed+" AVG Dale Chall Incorrect Std Dev Avg")

    writer.writerow(title_row)

    for prompt_file_name, extradata_summary in mega_summary.items():
        row_data=[prompt_file_name]
        for extradata_f_name, summary in extradata_summary.items():
            if extradata_f_name!="result" and extradata_f_name!="result_fklg" and extradata_f_name!="result_dale_chall" and extradata_f_name!="result_fklg_std_dev_avg" and extradata_f_name!="result_dale_chall_std_dev_avg":
                row_data.append(summary["result"])
                row_data.append(summary["result_fklg_correct"])
                row_data.append(summary["result_fklg_correct_std_dev_avg"])
                row_data.append(summary["result_fklg_incorrect"])
                row_data.append(summary["result_fklg_incorrect_std_dev_avg"])
                row_data.append(summary["result_dale_chall_correct"])
                row_data.append(summary["result_dale_chall_correct_std_dev_avg"])
                row_data.append(summary["result_dale_chall_incorrect"])
                row_data.append(summary["result_dale_chall_incorrect_std_dev_avg"])
        writer.writerow(row_data)