





import os
import json
import requests
import cloudinary.uploader
from   dotenv import load_dotenv
from   bs4    import BeautifulSoup as bs




# load environment variables from .env file
load_dotenv()

# cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
       api_key=os.getenv("CLOUD_KEY"   ),
    api_secret=os.getenv("CLOUD_SECRET"),
)


# helper function to fetch poster info and upload to Cloudinary
def fetch_and_upload_poster(imdb_id):
    """
    Fetches poster information from IMDb for a given imdb_id, uploads it to Cloudinary, 
    and returns a dictionary with title, IMDb ID, and Cloudinary ID.
    
    If the poster isn't available, returns 'no poster' for cloudinary_id.
    """
    
    try:

        url       = f"https://www.imdb.com/title/{imdb_id}/"
        headers   = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        
        }
        session   = requests.Session()
        response  = session.get(url, headers=headers)
        response.raise_for_status()

        # parse the page's HTML content
        soup      = bs(response.content, "lxml")
        film_json = soup.find("script", type="application/ld+json")

        # extract title and image information
        if film_json:
            json_dict      = json.loads(film_json.string)
            name           = json_dict.get("name", "")
            formatted_name = name.replace(" ", "_") + f"_{imdb_id}"
            image_url      = json_dict.get("image", "no poster")

            # If an image is found, upload to Cloudinary
            if image_url != "no poster":
                upload_result = cloudinary.uploader.upload(image_url, folder="posters/", public_id=formatted_name)
                image_ref     = upload_result.get("public_id", "no poster")
                print(f"Uploaded poster for {name} to Cloudinary with ID: {image_ref}")
                return {"title": name, "imdb_id": imdb_id, "cloudinary_id": image_ref}
            
            else:
                return {"title": name, "imdb_id": imdb_id, "cloudinary_id": "no poster"}
        else:
            return {"title": None, "imdb_id": imdb_id, "cloudinary_id": "no poster"}

    except requests.exceptions.RequestException as e:
        print(f"RequestException: {e}")
        return {"error": f"RequestException: {e}", "imdb_id": imdb_id}

    except Exception as e:
        print(f"An error occurred: {e}")
        return {"error": f"An error occurred: {e}", "imdb_id": imdb_id}


# Main function for processing IMDb credits
def process_new_credits(db_credits, imdb_credits):
    """
    Compares a list (credits already in the database) and a set (newly fetched IMDb credits).
    Identifies the new credits (those not in the list), fetches poster info for them,
    uploads to Cloudinary, and returns the results.
    
    Args:
        db_credits (list): Credits already in the database (from Step 1).
        imdb_credits (set): Newly fetched credits (from Step 2).
    
    Returns:
        list: List of dictionaries with title, imdb_id, and cloudinary_id.
    """
    try:
        if not db_credits or not imdb_credits:
            print("Both 'db_credits' and 'imdb_credits' must be provided.")
            return []

        # identify credits that are in IMDb credits but not in the database (new credits)
        new_credits = list(imdb_credits.difference(db_credits))

        if not new_credits:
            print("No new credits to process.")
            return []

        print(f"New credits to process: {new_credits}")

        # process each new credit and fetch the poster
        results = []
        for imdb_id in new_credits:
            result = fetch_and_upload_poster(imdb_id)
            results.append(result)

        return results

    except Exception as e:
        print(f"An error occurred during processing: {str(e)}")
        return []


if __name__ == "__main__":

    import sys

    # example usage: pass two arguments, 'db_credits' and 'imdb_credits'
    if len(sys.argv) < 3:
        print("Usage: python posters_handler.py <db_credits> <imdb_credits>")
        sys.exit(1)

    # simulating list and set inputs (can be passed in as arguments from GitHub Actions)
    db_credits       = json.loads(sys.argv[1])
    imdb_credits     = set(json.loads(sys.argv[2]))

    # run the main function
    new_credits_info = process_new_credits(db_credits, imdb_credits)

    # print out the results for each new credit
    print("New Credits Processed:")
    for credit in new_credits_info:
        print(credit)
