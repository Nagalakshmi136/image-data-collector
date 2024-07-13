import os
import sqlite3
import sys
from io import BytesIO

import requests
from PIL import Image
from tqdm import tqdm

from utils.file_utils import create_dir


def download_images(database: str, width: int, height: int) -> None:
    """Downloads images in the folder named data with the urls in the given database and
    updates database with image information like type, dimensions and size of image.

    Parameters:
    -----------
    database: `str`
        name of the database which contains image urls.
    width: `int`
        desired width of the image to download.
    height: `int`
        desired height of the image to download.
    """
    data_path = create_dir(f"{os.getcwd()}/data")
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute(
        "SELECT image_url,image_category,image_id FROM images WHERE image_dimensions is NULL"
    )
    image_urls = cursor.fetchall()
    print(len(image_urls))
    for image_url in tqdm(image_urls):
        try:
            response = requests.get(image_url[0], stream=True, timeout=(30, 60))
            print("get response")
            content_type = response.headers["content-type"]
            image_content = response.content
            image = Image.open(BytesIO(image_content))
            image_dimensions = f"{image.width} X {image.height}"
            image_size = f"{sys.getsizeof(image_content)/1024} kb"
            cursor.execute(
                "UPDATE images SET image_type=?, image_dimensions=?, image_size=? WHERE image_url=?",
                (content_type, image_dimensions, image_size, image_url[0]),
            )
            print("updated")
            connection.commit()
            image_category_path = create_dir(f"{data_path}/{image_url[1]}")
            resized_image = image.resize((width, height))
            resized_image.save(
                f"{image_category_path}/{image_url[1]}{image_url[2]}.jpeg"
            )
        except Exception as e:
            print(e)
            continue
    connection.close()
