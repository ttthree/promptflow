from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_fixed

@retry(stop=stop_after_attempt(1), wait=wait_fixed(2))
def scrape(url, timeout_sec=10):
    """
    Fetch the content of a URL and parse it and return the content as a string.

    :param url: str, the URL to fetch and parse.
    """
    options = Options()
#    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    driver.set_page_load_timeout(timeout_sec)
    try:
        driver.get(url)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        content = soup.get_text()

        # Remove duplicated whitespace
        content = " ".join(content.split())

        driver.quit()

        return content
    except Exception as e:
        driver.quit()
        return ""
    
if __name__ == '__main__':
    url = "https://www.forbes.com/sites/alexkonrad/2024/03/19/inflection-abandons-chatgpt-challenger-ceo-suleyman-joins-microsoft/"
    content = scrape(url)
    print(content)
    

