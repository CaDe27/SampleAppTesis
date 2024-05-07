import concurrent.futures
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import requests
import shutil
import os
import base64
import csv

waiting_time = 20
sleeping_time = 2

def get_img_class_debugger():
    image_elements = driver.find_elements(By.TAG_NAME, 'img')
    img_classes = set()
    for i, img in enumerate(image_elements, start=1):
        # Retrieve the class attribute of each image
        image_class = img.get_attribute('class')
        img_classes.add(image_class)
    print(f"{img_classes}")

def clean_driver():
    driver = webdriver.Chrome()
    driver.quit()

def download_movie_image(movie_tuple, indx):
    save_path = "./movie_images"
    os.makedirs(save_path, exist_ok=True)  # Ensure the save directory exists
    image_downloaded = False # Flag to track if the image download was successful
    try:
        # Google Image search URL
        id = movie_tuple[0]
        movie = movie_tuple[1]
        movie = movie.replace("(", "")
        movie = movie.replace(")", "")
        movie = movie.replace("&", "and")
        movie_search = movie.replace(" ", "+")
        search_url = f"https://www.google.com/search?hl=en&tbm=isch&q={movie_search}+movie"
        driver.get(search_url)
    
        # Find and click on the first image element to open the preview
        first_image = driver.find_element(By.XPATH, "//img[contains(@class, 'rg_i Q4LuWd') or starts-with(@class, 'YQ4gaf')]")
        first_image.click()
        time.sleep(sleeping_time)

        # Locate the larger version of the image within the preview pane
        large_image = driver.find_element(By.XPATH, '//img[contains(@class, "sFlh5c pT0Scc iPVvYb")]')
        image_url = large_image.get_attribute('src')
        # time.sleep(sleeping_time)

        # Download the image
        if image_url.startswith('http'):
            response = requests.get(image_url, stream=True)
            file_path = os.path.join(save_path, f"{id}.jpg")
            with open(file_path, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
        else:
            # It's a base64 encoded image
            base64_string = image_url.split(',')[1]
            file_path = os.path.join(save_path, f"{id}.jpg")
            with open(file_path, "wb") as out_file:
                out_file.write(base64.b64decode(base64_string))
        image_downloaded = True
    except (NoSuchElementException, ElementClickInterceptedException) as e:
        print(f"Failed to find or click image for {movie}: {e}")
    except Exception as e:
        print(f"An error occurred while processing {movie}: {e}")
    if not image_downloaded:
        print(f"Image was not downloaded for {indx} id: {id} movie: {movie}.")

def read_movie_tuples():
    # List of movies - this should be your list of 848 movies
    movies_tuples = []
    count = 0
    #    with open('./data/movies.csv', newline='') as csvfile:
    with open('./content_movie_list.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for line in reader:
            if count == 0:
                count += 1  #skip header
                #print(line) print
            else:
                count += 1
                movie_id = int(line[0])
                movie_title = line[1]
                movies_tuples.append((movie_id, movie_title))
                #movie_dict[movie_id]["title"] = line[1]
                #movie_dict[movie_id]["genres"] = line[2]
    return movies_tuples

movies_tuples = read_movie_tuples()
start = 769
movies_tuples = movies_tuples[start:]

driver = webdriver.Chrome()
start_time = time.time()
for indx, movie_tuple in enumerate(movies_tuples, start=start):
    download_movie_image(movie_tuple, indx)
end_time = time.time()
driver.quit()
print(f"Downloaded images for {len(movies_tuples)} movies in {end_time - start_time} seconds.")
