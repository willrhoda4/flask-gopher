





import requests             # For making HTTP requests to the Node API
import os                   # For fetching environment variables
import json                 # For handling JSON data
import cloudinary.uploader  # For uploading images to Cloudinary




# function to upload a movie poster to Cloudinary
def upload_poster_to_cloudinary( poster_url, title, imdb_id ):
   
    # upload the poster to Cloudinary and return the public Cloudinary ID
    # the public ID is based on the title and IMDb ID to ensure uniqueness
    response = cloudinary.uploader.upload( poster_url, public_id=f'posters/{title}_{imdb_id}' )
    
    # extract the Cloudinary public ID from the response
    return response.get('public_id')




# function to send updated credits back to the Node API
def update_credits_on_node(credits, api_url, token):
   
    #set up the headers with the authorization token for secure API access
    headers = {
        'Authorization': f'Bearer {token}',  # insert the token in the Authorization header
        'Content-Type': 'application/json'   # specify that the content being sent is JSON
    }

    # send the updated credits data as a POST request to the Node API
    response = requests.post(api_url, json=credits, headers=headers)

    # check if the response status code is 200 (OK)
    if response.status_code == 200:
        print("Successfully updated credits on Node API")
    else:
        # Print an error message if the credits could not be updated
        print(f"Error updating credits: {response.status_code}")




# main function to fetch new credits, upload posters, and update credits on Node API
if __name__ == "__main__":
   
    # fetch the Node API URL and GitHub token from environment variables (these will be set in GitHub Actions)
    node_api_url = os.getenv('NODE_API_URL', 'http://localhost:5000')  # Default API URL
    github_token = os.getenv('GITHUB_TOKEN')  # Token for secure access to the Node API

    # simulated new credits from IMDb (replace this with the actual scraped data)
    new_credits = [
        {
            "imdb_id": "tt1234567",
            "title": "New Movie",
            "poster_url": "https://imdb.com/some_poster.jpg"
        }
    ]

    # Initialize an empty list to store updated credits
    updated_credits = []

    # Loop through each new credit
    for credit in new_credits:
        # Upload the poster to Cloudinary and get the Cloudinary public ID
        cloudinary_id = upload_poster_to_cloudinary(credit['poster_url'], credit['title'], credit['imdb_id'])

        # Append the IMDb ID, title, and Cloudinary public ID to the updated credits list
        updated_credits.append({
            "imdb_id": credit['imdb_id'],
            "title": credit['title'],
            "cloudinary_id": cloudinary_id
        })

    # Send the updated credits to the Node API for updating the credits table
    update_credits_on_node(updated_credits, node_api_url, github_token)

