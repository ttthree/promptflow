from promptflow.core import Flow
from promptflow.tracing import start_trace, trace
from dotenv import load_dotenv
import os

@trace
def eval_correctness(question: str, answer: str, groundtruth: str) -> dict:
    """
    Evaluate the correctness of the answer to the question based on the ground truth.

    :param question: str, the question.
    :param answer: str, the answer to the question.
    :param ground_truth: str, the ground truth answer to the question.

    :return: float, the correctness of the answer, 0 means incorrect, 1 means correct.
    """
    # Load the correctness evaluation flow from the same folder as the current script.
    eval = Flow.load(os.path.dirname(__file__) + '/correctness.prompty')
    return eval(question=question, answer=answer, ground_truth=groundtruth)

if __name__ == '__main__':
    load_dotenv(override=True)
    start_trace()

    question = "Who is the CEO of Inflection AI?"
    answer = "Mustafa Suleyman"
    ground_truth = "Sean White is the CEO of Inflection AI."

    result = eval_correctness(question, answer, ground_truth)
    print(result)

    answer = "Sean White"
    ground_truth = "After Mustafa Suleyman left, Sean White became the CEO of Inflection AI."
    result = eval_correctness(question, answer, ground_truth)
    print(result)

    answer = "After Mustafa Suleyman left, Sean White became the CEO of Inflection AI."
    ground_truth = "Sean White is the CEO of Inflection AI."
    result = eval_correctness(question, answer, ground_truth)
    print(result)
