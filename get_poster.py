





import os
import json
import requests
from   bs4 import BeautifulSoup as bs
import cloudinary.uploader
from   dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


# Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET"),
)

def get_poster(imdb_id):



    try:
        url = f"https://www.imdb.com/title/{imdb_id}/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        session = requests.Session()
        response = session.get(url, headers=headers)
        response.raise_for_status()
        
        soup = bs(response.content, "lxml")
        film_json = soup.find("script", type="application/ld+json")
        
        if film_json:
            json_dict = json.loads(film_json.string)
            name = json_dict.get("name", "")
            formatted_name = name.replace(" ", "_") + f"_{imdb_id}"
            image_url = json_dict.get("image", "no poster")
            
            if image_url != "no poster":
                # Upload the image to Cloudinary with the formatted name
                upload_result = cloudinary.uploader.upload(image_url, folder="posters/", public_id=formatted_name)
                image_ref = upload_result.get("public_id", "no poster")
                print(f"Uploaded poster for {name} to Cloudinary with ID: {image_ref}")
                
                # Return the formatted title and image_ref (public ID)
                return [name, image_ref]
            else:
                print(f"No poster found for {name}")
        else:
            print("No valid film JSON found on the page")

    except requests.exceptions.RequestException as e:
        print(f"RequestException: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    imdb_id = "tt0923293"
    get_poster(imdb_id)






