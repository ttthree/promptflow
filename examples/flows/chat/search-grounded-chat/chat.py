import os
from promptflow.tracing import trace, start_trace
from promptflow.core import Flow
from search import search
from dotenv import load_dotenv

@trace
def chat(question: str, history: list=[]):
    max_search_rounds = int(os.environ.get('MAX_ROUND_OF_SEARCH'))
    model_provider = os.environ.get('MODEL_PROVIDER')
    extract = Flow.load(f'extract_search_query_{model_provider}.prompty')
    answer = Flow.load(f'answer_question_{model_provider}.prompty')

    print(f"Using model provider: {model_provider}")

    round = 0
    need_search = True
    context = []
    while round < max_search_rounds and need_search:
        round += 1
        query = extract(question=question, context=context, history=history)
        need_search = bool(query['NeedSearch'])
        if need_search:
            for item in search(query['Query'], top_k=3):
                context.append(item)

    result = answer(question=question, context=context, history=history)

    return {"output": result}
    
if __name__ == '__main__':
    load_dotenv(override=True)
    start_trace()

    history = []
    while True:
        question = input("\033[92m" + "$User (type q! to quit): " + "\033[0m")
        if question == "q!":
            break

        answer = chat(question, history)

        print("\033[92m" + "$Bot: " + "\033[0m", end=" ", flush=True)
        print(answer["output"])
        print(flush=True)

        history.append({"role":"user", "content": question})
        history.append({"role":"assistant", "content": answer["output"]})