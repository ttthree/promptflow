from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
from bs4 import BeautifulSoup
from promptflow.tracing import trace
from tenacity import retry, stop_after_attempt, wait_fixed

@trace
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def scrape(url):
    """
    Fetch the content of a URL and parse it and return the content as a string.

    :param url: str, the URL to fetch and parse.
    """
    options = Options()
    options.headless = True
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    driver.get(url)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    content = soup.get_text()

    return content

    driver.quit()

