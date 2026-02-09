#!/bin/sh

if [ "$1" != "--ollama_url" ] || [ -z "$2" ]; then
    echo "Usage: $0 --ollama_url <ollama_url>"
    exit 1
fi

models=("GEMMA_3_27B" "LLAMA_3_3_70B" "DEEPSEEK_R1_70B" "MISTRAL_123B")
ollama_url=$2

error_flag=false

python create_dataset.py
if [ $? -ne 0 ]; then
    error_flag=true
fi

if [ $error_flag = true ]; then
    echo "An error occurred during dataset creation."
    exit 1
fi

for i in "${models[@]}"
do
   /bin/sh run_evaluate_model.sh --model $i --ollama_url $ollama_url
done