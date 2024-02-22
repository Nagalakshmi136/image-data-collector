import requests
import sqlite3
import os
import sys
from PIL import Image
from io import BytesIO

def create_dir(dir_path: str):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path
    
def fetch_images(database: str, width: int, height: int):
    data_path = create_dir(f'{os.getcwd()}/data')
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("SELECT image_url,image_category FROM images WHERE image_dimensions is NULL")
    image_urls = cursor.fetchall()
    for ind,image_url in enumerate(image_urls):
        try:
            response = requests.get(image_url[0],stream=True)
            content_type =response.headers['content-type']
            image_content = response.content
            image = Image.open(BytesIO(image_content))
            image_dimensions = f'{image.width} X {image.height}'
            image_size = f'{sys.getsizeof(image_content)/1024} kb'
            cursor.execute("UPDATE images SET image_type=?, image_dimensions=?, image_size=? WHERE image_url=?",(content_type,image_dimensions,image_size,image_url[0]))
            connection.commit()
            image_category_path = create_dir(f'{data_path}/{image_url[1]}')
            resized_image = image.resize((width,height))
            resized_image.save(f'{image_category_path}/{image_url[1]}{ind}.jpeg')
        except Exception as e:
            print(e)
            continue
    connection.close()