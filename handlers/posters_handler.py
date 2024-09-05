





import os
import json
import requests
import cloudinary.uploader
from   dotenv import load_dotenv
from   flask  import request, jsonify
from   bs4    import BeautifulSoup as bs






# Load environment variables from .env file
load_dotenv()


# Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET"),
)


def get_poster():
    
        
    try:
        # Extract the imdbId from the request JSON
        data = request.json
        imdb_id = data.get("imdbId")

        # Perform any processing here with the imdb_id
        if not imdb_id:
            return jsonify({"error": "imdbId is required"}), 400

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
                return jsonify({"title": name, "image_ref": image_ref}), 200
            else:
                return jsonify({"error": f"No poster found for {name}"}), 404
        else:
            return jsonify({"error": "No valid film JSON found on the page"}), 400

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"RequestException: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
