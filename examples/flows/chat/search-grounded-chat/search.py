import requests
import os
from bs4 import BeautifulSoup
from promptflow.tracing import trace
from tenacity import retry, stop_after_attempt, wait_fixed

from scrape import scrape

def search(query: str, top_k: int):
    # Search for the top_k most relevant web page results for the query.
    if os.environ.get('SEARCH_PROVIDER') is None or os.environ.get('SEARCH_API_KEY') is None:
        raise ValueError("Please set the SEARCH_PROVIDER and SEARCH_API_KEY environment variables.")
    
    search_provider = os.environ.get('SEARCH_PROVIDER')

    if search_provider.lower() == 'bing':
        search_results = search_bing(query, top_k)
    else:
        raise ValueError(f"Unsupported search provider: {search_provider}")

    return search_results

# Search Bing with Bing API and return the top n results, each entry with the title of the page, the URL, the snippet of the page and the content of the page.
@trace
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def search_bing(query, n=5):
    """
    Search Bing with Bing API and return the top n results, each entry with the title of the page, the URL, the snippet of the page and the content of the page.

    :param query: str, the query to search.
    :param n: int, the number of results to return.
    """
    api_key = os.environ.get('SEARCH_API_KEY', "NO_API_KEY").strip()  # Ensure your API key is stored in an environment variable
    if api_key == 'NO_API_KEY':
        raise ValueError("API key is not set correctly.")

    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
        "Accept": "application/json"   
    }
    params = {
        "q": query,
        "count": n,
        "mkt": "en-US",
#        "safesearch": "Moderate",
#        "textDecorations": True,
#        "textFormat": "HTML"
    }
    search_url = "https://api.bing.microsoft.com/v7.0/search"

    response = requests.get(search_url, headers=headers, params=params)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {response.text}")
        return []
    search_results = response.json()

    results = []
    for result in search_results.get("webPages", {}).get("value", []):
        entry = {
            "title": result.get("name"),
            "URL": result.get("url"),
            "snippet": result.get("snippet"),
            "content": scrape(result.get("url"))
            # Note: Directly fetching the content of the page is not provided by the Bing API.
            # You would need to make separate requests to each URL to get the full content,
            # which can be complex and is subject to the website's `robots.txt` rules.
        }
        results.append(entry)

    return results

if __name__ == "__main__":
    import dotenv
    from promptflow.tracing import start_trace

    start_trace()
    dotenv.load_dotenv()

    query = "Who are the boarder members of OpenAI?"
    top_k = 3
    search_results = search(query, top_k)
    for i, result in enumerate(search_results):
        print(f"Result {i+1}:")
        print(f"Title: {result['title']}")
        print(f"URL: {result['URL']}")
        print(f"Snippet: {result['snippet']}")
        print(f"Content: {result['content'][:100]}...")
        print()
