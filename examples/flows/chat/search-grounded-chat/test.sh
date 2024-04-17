# run the chat flow
dotenv run pf run create --flow flow.flex.yaml --inputs test_data.jsonl

# run correctness evaluation
dotenv run pf run create --flow ./evals/correctness/flow.flex.yaml --run search_grounded_chat_variant_0_20240417_135355_388094 --column-mapping question='${data.question}' answer='${run.outputs.output}' groundtruth='${data.ground_truth}' --data test_data.jsonl