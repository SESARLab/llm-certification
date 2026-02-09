#!/bin/sh

if [ "$1" != "--model" ] || [ -z "$2" ] || [ "$3" != "--ollama_url" ] || [ -z "$4" ] ; then
    echo "Usage: $0 --model <model_name> --ollama_url <ollama_url>"
    exit 1
fi

model=$2
ollama_url=$4

declare -A models_map

models_map=(
    ["GEMMA_3_27B"]="gemma3:27b-it-q4_K_M"
    ["LLAMA_3_3_70B"]="llama3.3:70b-instruct-q5_K_M"
    ["DEEPSEEK_R1_70B"]="deepseek-r1:70b"
    ["MISTRAL_123B"]="mistral-large:123b-instruct-2411-q5_K_M"
)

first_iteration=true
error_flag=false

while [ $error_flag = true ] || [ $first_iteration = true ] ; do
    echo "Starting evaluation..."
    curl -k $ollama_url -d '{"model": "'"${models_map[$model]}"'", "keep_alive": -1}'
    if [ $? -ne 0 ]; then
        error_flag=true
    else
        error_flag=false
    fi
    if [ $error_flag = false ]; then
        python submit_to_model.py --model $model --ollama_url $ollama_url
        if [ $? -ne 0 ]; then
            error_flag=true
        else
            error_flag=false
        fi
        if [ $error_flag = false ]; then
            python evaluate_model.py --model $model
            if [ $? -ne 0 ]; then
                error_flag=true
            else
                error_flag=false
            fi
            if [ $error_flag = false ]; then
                python analyze_results_quality.py --model $model
                python analyze_results_time.py --model $model
                if [ $? -ne 0 ]; then
                    error_flag=true
                else
                    error_flag=false
                fi
                if [ $error_flag = false ]; then
                    curl -k $ollama_url -d '{"model": "'"${models_map[$model]}"'", "keep_alive": 0}'
                    if [ $? -ne 0 ]; then
                        error_flag=true
                    else
                        error_flag=false
                    fi
                fi
            fi
        fi
    fi
    first_iteration=false
    if [ $error_flag = true ]; then
        echo "An error occurred, retrying..."
    else
        echo "Evaluation completed successfully."
    fi
done