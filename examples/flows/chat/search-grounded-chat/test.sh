#!/bin/bash

# run the chat flow
output=$(dotenv run pf run create --flow flow.flex.yaml --data test_data.jsonl)

# exit if the command above failed
if [ $? -ne 0 ]; then
  echo "Failed to run the chat flow"
  exit 1
fi

# once the command above finish the stdout will contain the run id which is looks like "run": "search_grounded_chat_variant_0_20240417_135355_388094"
# we will parse the run id and use it to evaluate the correctness of the chat flow
echo "$output"
run_id=$(echo "$output" | awk -F'"' '/"name":/ {print $4}')

# if unable to parse the run id, exit
if [ -z "$run_id" ]; then
  echo "Failed to parse the run id"
  exit 1
fi

echo "$run_id"

# run correctness evaluation
dotenv run pf run create --flow ./evals/correctness/flow.flex.yaml --run "$run_id" --column-mapping question='${data.question}' answer='${run.outputs.output}' groundtruth='${data.ground_truth}' --data test_data.jsonl

echo $?