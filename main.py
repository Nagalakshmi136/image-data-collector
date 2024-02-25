from fetch_image_urls import fetch_image_urls
from fetch_images import fetch_images

# fetch_image_urls(input_file='input_data.csv')
fetch_images(database="images_data.db",width=512,height=512)
