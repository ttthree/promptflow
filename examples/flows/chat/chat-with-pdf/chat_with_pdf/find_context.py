import faiss
from jinja2 import Environment, FileSystemLoader
import os

from utils.index import FAISSIndex
from utils.oai import OAIEmbedding, render_with_token_limit
from utils.logging import log
from promptflow.tracing import trace


@trace
def find_context(question: str, index_path: str):
    index = FAISSIndex(index=faiss.IndexFlatL2(1536), embedding=OAIEmbedding())
    index.load(path=index_path)
    snippets = index.query(question, top_k=50)

    template = Environment(
        loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__)))
    ).get_template("qna_prompt.md")
    token_limit = int(os.environ.get("PROMPT_TOKEN_LIMIT"))

    # Try to render the template with token limit and reduce snippet count if it fails
    while True:
        try:
            prompt = render_with_token_limit(
                template, token_limit, question=question, context=enumerate(snippets)
            )
            break
        except ValueError:
            snippets = snippets[:-1]
            log(f"Reducing snippet count to {len(snippets)} to fit token limit")

    # sort the context by page number
    snippets = sorted(snippets, key=lambda c: c.metadata)

    # render again as we now sorted the snippets based on page number
    prompt = render_with_token_limit(template, token_limit, question=question, context=enumerate(snippets))

    return prompt, snippets
