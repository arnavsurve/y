import os
import time
from logging import error

from alive_progress import alive_bar
from bs4 import BeautifulSoup
from lsd import lsd_conn
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from utils.cleaning import clean_text
from yaspin import yaspin
from yaspin.spinners import Spinners

url = "https://www.tetragrammaton.com/articles"
article_extensions = set()
articles_data = []


with yaspin(Spinners.earth, text="Loading Chrome webdriver") as sp:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    service = Service()  # type: ignore
    driver = webdriver.Chrome(service=service, options=chrome_options)

with yaspin(Spinners.earth, text="Traversing links") as sp:
    driver.get(url)

    scroll_pause_time = 2
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break
        last_height = new_height

    soup = BeautifulSoup(driver.page_source, "html.parser")

    driver.quit()

    for a in soup.find_all("a", href=True):
        if a["href"].startswith("/content"):  # type: ignore
            article_extensions.add(a["href"].split("#")[0])  # type: ignore


with alive_bar(len(article_extensions), spinner="dots_waves", title_length=60) as bar:
    for extension in article_extensions:
        sub_url = f"https://www.tetragrammaton.com{extension}"
        bar.title(f"Parsing {sub_url}")

        output_file = f"../datasets/raw/{extension}.txt"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with lsd_conn.cursor() as curs:
            curs.execute(
                f"""
                FROM {sub_url}
                |> SELECT TEXT as text
                """
            )
            res = curs.fetchone()

            try:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(
                        "URL: {sub_url}\n" + clean_text(res[0])
                        if res
                        else bar.title("No text found")
                    )
            except Exception as e:
                error(f"Error writing to file: {e}")
                continue

        bar()
