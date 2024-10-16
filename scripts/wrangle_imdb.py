





import requests                   # for making HTTP requests to the Node API
import os                         # for fetching environment variables
import json                       # for handling JSON data
from   dotenv import load_dotenv  # import the load_dotenv function from the dotenv package

load_dotenv()                     # load environment variables from the .env file


# function to fetch IMDb IDs from the Node API
def fetch_imdb_ids(api_url, token):

    print('Fetching IMDb IDs for the team...')

    # set up the headers with the authorization token for secure API access
    headers = {
        'Authorization': f'Bearer {token}',  # insert the token in the Authorization header
        'Content-Type': 'application/json'   # specify that the content being sent is JSON
    }   

    # make a GET request to the Node API to fetch the IMDb IDs
    response = requests.get( api_url, headers=headers )

    # check if the response status code is 200 (OK)
    if response.status_code == 200:
        # parse the JSON response and return the IMDb IDs for team members and credits
        data = response.json()
        return data['team'], data['credits']
    
    else:
        # if the response is not OK, raise an error with the status code for proper handling
        raise Exception(f"Error fetching IMDb IDs: {response.status_code}")

# main function that will be executed when the script is run
def main():
    
    
    try:
        # fetch the Node API URL and GitHub token from environment variables (these will be set in GitHub Actions)
        api_url      = os.getenv('NODE_API_URL', 'http://localhost:5000')  # default API URL
        github_token = os.getenv('GITHUB_TOKEN')                            # token for secure access to the Node API

        # fetch the IMDb IDs from the Node API and return as a tuple
        return fetch_imdb_ids(f"{api_url}/wrangleImdbIds", github_token)

    except Exception as e:
        # if an error occurs, print the error (this will show up in the GitHub Actions log)
        print(str(e))
        # return None, None for error cases
        return None, None

# ensure the script can be executed if run directly
if __name__ == "__main__":
    team_ids, credit_ids = main()  # Unpack the tuple result

    # print the result in JSON format for logging or passing to the next step
    print( json.dumps( { "team_ids": team_ids, "credit_ids": credit_ids } ) )
