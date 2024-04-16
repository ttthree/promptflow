import requests
import os
from bs4 import BeautifulSoup
from promptflow.tracing import trace
from tenacity import retry, stop_after_attempt, wait_fixed
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

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
def search_bing(query, n):
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

    with ThreadPoolExecutor(max_workers=2) as executor:
        web_future = executor.submit(perform_bing_web_search, headers, params)
        news_future = executor.submit(perform_bing_news_search, headers, params)

    web_results = web_future.result()
    news_results = news_future.result()
    
    return web_results + news_results

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def perform_bing_web_search(headers, params):
    
    response = requests.get("https://api.bing.microsoft.com/v7.0/search", headers=headers, params=params)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {response.text}")
        return []
    search_results = response.json()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(scrape, result.get("url")): result for result in search_results.get("webPages", {}).get("value", [])}

    results = []
    for future in concurrent.futures.as_completed(futures):
        result = futures[future]
        try:
            content = future.result()
        except Exception as exc:
            print(f"Generated an exception: {exc}")
        else:
            entry = {
                "title": result.get("name"),
                "URL": result.get("url"),
                "snippet": result.get("snippet"),
                "content": content
            }
            results.append(entry)

    return results

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def perform_bing_news_search(headers, params):
    
    response = requests.get("https://api.bing.microsoft.com/v7.0/news/search", headers=headers, params=params)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {response.text}")
        return []
    search_results = response.json()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(scrape, result.get("url")): result for result in search_results.get("value", [])}

    results = []
    for future in concurrent.futures.as_completed(futures):
        result = futures[future]
        try:
            content = future.result()
        except Exception as exc:
            print(f"Generated an exception: {exc}")
        else:
            entry = {
                "title": result.get("name"),
                "URL": result.get("url"),
                "snippet": result.get("description"),
                "content": content
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
