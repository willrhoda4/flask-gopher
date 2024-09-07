import json
import requests
from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv
import os

# Load environment variables (if any)
load_dotenv()

def scrape_imdb(team_and_credits_file):
    try:
        # Load the team and credits data
        with open(team_and_credits_file, 'r') as f:
            team_data = json.load(f)

        imdb_credits = set()
        team = team_data.get('team', [])

        for member in team:
            imdb_url = f"https://www.imdb.com/name/{member}/?showAllCredits=true"
            print(f"Scraping URL: {imdb_url}")
            response = requests.get(imdb_url)
            response.raise_for_status()
            soup = bs(response.content, 'html.parser')

            # Extract the credits from the IMDb page
            stunt_credits = soup.find_all("li", {"data-testid": "credit_stunts"})
            for credit in stunt_credits:
                href = credit.find('a', href=True)['href']
                imdb_id = href.split('/')[2]  # Extract the IMDb ID (ttXXXXXXX)
                imdb_credits.add(imdb_id)

        # Save the new credits to a file
        new_credits = list(imdb_credits)
        with open('new_credits.json', 'w') as f:
            json.dump(new_credits, f)
        
        print(f"Scraping complete. Found {len(new_credits)} new credits.")

    except Exception as e:
        print(f"An error occurred while scraping IMDb: {e}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python update_barn.py <team_and_credits_file>")
    else:
        scrape_imdb(sys.argv[1])

