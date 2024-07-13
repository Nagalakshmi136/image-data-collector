from fetch_image_urls import fetch_image_urls
from fetch_images import download_images
from utils.db_utils import Database

# db = Database('images_data.db')
# ls = db.count_column1_per_column2('image_url','image_category','images')
# db.close_connection()
fetch_image_urls(database='images_data.db',input_file='input_data.csv')
# download_images(database="images_data.db",width=512,height=512)
