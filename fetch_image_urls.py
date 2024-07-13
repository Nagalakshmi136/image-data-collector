import sqlite3
import time
from typing import List

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm


def fetch_image_urls(input_file: str, database: str):
    """Fetch image urls and tiles for all the queries in the input_file from the google and stores them in database.

    Parameters:
    -----------
    input_file: `str`
        path to the input file(format: csv) which contains list of desired query, max_limit, width, height of the images.
    database: `str`
        Database name if don't exist it will create a new one.
    """
    # Load input data about images from csv file
    df = pd.read_csv(input_file)
    # Creates a Database to store image urls
    connection = sqlite3.connect(f"{database}.db")
    cursor = connection.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS images(
                    image_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_url TEXT NOT NULL UNIQUE,
                    image_category TEXT,
                    image_title TEXT,
                    image_type TEXT,
                    image_dimensions TEXT,
                    image_size TEXT
                )"""
    )
    connection.commit()
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    wait = WebDriverWait(driver, 10)

    def scroll_to_bottom():
        """This will scroll the webpage to the bottom to load all the images in the page."""

        last_height = driver.execute_script(
            "\
            return document.body.scrollHeight"
        )

        while True:
            driver.execute_script(
                "\
                window.scrollTo(0,document.body.scrollHeight)"
            )

            # waiting for the results to load
            # Increase the sleep time if your internet is slow
            time.sleep(5)

            new_height = driver.execute_script(
                "\
                return document.body.scrollHeight"
            )

            # click on "Show more results" (if exists)
            try:
                more_results = wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//input[@value="Show more results"]')
                    )
                )
                more_results.click()
                # waiting for the results to load
                # Increase the sleep time if your internet is slow
                time.sleep(5)

            except:
                pass

            # checking if we have reached the bottom of the page
            if new_height == last_height:
                break
            last_height = new_height
            break

    def fetch_urls(query: str, max_limit: int) -> List[str]:
        """This fetches max_limit number of image urls of the given query.

        Parameters:
        -----------
        query: `str`
            image name (eg: cats).
        max_limit: `int`
            maximum number of images you desired to retrieve.

        Return:
        -------
        List[str]
            list of image urls of the given query.
        """

        # Open Google Images in the browser
        driver.get("https://images.google.com/")
        # Finding the search box
        box = wait.until(
            EC.presence_of_element_located((By.XPATH, '//textarea[@id="APjFqb"]'))
        )

        # Type the search query in the search box
        box.send_keys(query)

        # Pressing enter
        box.send_keys(Keys.ENTER)

        # Function for scrolling to the bottom of Google
        # Images results
        scroll_to_bottom()
        images_path = '//img[contains(@class,"YQ4gaf")]'
        image_results = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, images_path))
        )
        return image_results[0:max_limit]

    for ind in tqdm(df.index):
        query = df["keyword"][ind]
        max_limit = df["max_limit"][ind]
        urls = fetch_urls(query, max_limit)
        print(len(urls))
        count = 0
        for url in urls:
            try:
                url.click()
                actual_img_path = '//img[@class="sFlh5c pT0Scc iPVvYb"]'
                actual_image = wait.until(
                    EC.presence_of_element_located((By.XPATH, actual_img_path))
                )
                image_link = actual_image.get_attribute("src")
                if "http" in image_link:
                    cursor.execute(
                        """INSERT OR IGNORE INTO images (image_url, image_category, image_title, image_type, 
                                   image_dimensions,image_size) VALUES (?,?,?,NULL,NULL,NULL);""",
                        (image_link, query, actual_image.get_attribute("alt")),
                    )
                    connection.commit()
                    count += 1
            except Exception as e:
                print(e)
                continue
        print(count)
    connection.close()
