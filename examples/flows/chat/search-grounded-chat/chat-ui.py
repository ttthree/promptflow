import chainlit as cl

import os
from promptflow.tracing import trace, start_trace
from promptflow.core import Flow
from search import search

history = []

start_trace()

@trace
@cl.step
async def search_and_browse(question, history, max_search_rounds) -> list:
    context = []
    round = 0
    need_search = True
    extract = Flow.load('extract_search_query.prompty')
    while round < max_search_rounds and need_search:
        round += 1
        query = await cl.make_async(extract)(question=question, context=context, history=history)
        need_search = bool(query['NeedSearch'])
        if need_search:
            search_results = await cl.make_async(search)(query['Query'], top_k=3)
            for item in search_results:
                context.append(item)

    return context

@trace
@cl.step
async def chat(question: str, history: list, context: list):
    answer = Flow.load('answer_question.prompty')
    result = await cl.make_async(answer)(question=question, context=context, history=history)
    return result

@cl.on_message  # this function will be called every time a user inputs a message in the UI
async def main(message: cl.Message):
    """
    This function is called every time a user inputs a message in the UI.
    It sends back an intermediate response from the tool, followed by the final answer.

    Args:
        message: The user's message.

    Returns:
        None.
    """
    max_search_rounds = int(os.environ.get('MAX_ROUND_OF_SEARCH'))

    question = message.content

    context = await search_and_browse(question=question, history=history, max_search_rounds=max_search_rounds)

    result = await chat(question=question, history=history, context=context)

    history.append({"role":"user", "content": question})
    history.append({"role":"assistant", "content": result})

    # Send the final answer.
    await cl.Message(content=result).send()