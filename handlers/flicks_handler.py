





import re
import json
import argparse  # for argument parsing
import requests
from   playwright.sync_api import sync_playwright
from   bs4                 import BeautifulSoup     as bs




# function to fetch stunt credits for a specific IMDb member
def fetch_stunt_credits(member):
    """Fetch stunt credits from an IMDb member's page.

    Args:
        member (str): IMDb ID of the member (e.g., 'nm1819605')

    Returns:
        list: List of HTML elements that contain stunt credits
    """
    with sync_playwright() as playwright:
        # Launch browser in headless mode
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
                'Upgrade-Insecure-Requests': '1',
                'DNT': '1',
                'Referer': 'https://www.google.com/'
            }
        )
        page = context.new_page()

        url = f"https://www.imdb.com/name/{member}/?showAllCredits=true"

        try:
            # Open the IMDb page with extended timeout and network idle wait
            page.goto(url, wait_until="networkidle", timeout=90000)
            print(f"Fetching credits for {member}...")

            # Scroll through the page to trigger dynamic loading
            page.mouse.wheel(0, 2000)
            page.wait_for_timeout(2000)  # Give some time for scrolling to take effect

            # Wait for the section with 'Stunts' text to load
            page.wait_for_selector("hgroup h3:has-text('Stunts')", timeout=90000)
            print("Stunts section loaded.")

            # Extract <li> elements related to stunts
            li_elements = page.evaluate(
                """
                () => {
                    return Array.from(document.querySelectorAll("li[data-testid*='credit_stunts']")).map(li => li.outerHTML);
                }
                """
            )

            if li_elements:
                print(f"Found {len(li_elements)} stunt elements")
                return li_elements
            else:
                print("No elements found on the page.")
                print(page.content())  # Log the entire page content for debugging
                return []

        except playwright.TimeoutError:
            print(f"Timeout occurred while waiting for stunts section on {url}")
            return []
        except Exception as e:
            print(f"An error occurred in the fetch_stunt_credits function: {str(e)}")
            return []
        finally:
            browser.close()





# function to process a list of team IMDb IDs and fetch their stunt credits
def get_flicks(team):
    """Fetch stunt credits for each team member in the provided IMDb ID list.

    Args: 
        team (list): List of IMDb IDs (e.g., ['nm1819605', 'nm0743332'])

    Returns:
        tuple: Total credits count and list of unique film IMDb IDs
    """
    try:
        all_films = []

        print(f"Team list received: {team}")

        # loop through the team IMDb IDs and fetch credits for each member
        for member in team:
            stunt_elements = fetch_stunt_credits(member)
            print(f"Processing {len(stunt_elements)} stunt elements for {member}")

            # extract film IDs (IMDb tt numbers) from the HTML elements
            film_ids   = [re.search(r"tt\d+", li).group() for li in stunt_elements]
            all_films += film_ids

        # total credits and unique films
        total_credits = len(all_films)
        unique_films  = list(set(all_films))  # use set to remove duplicates

        print(f"Total Credits: {total_credits}")

        return total_credits, unique_films

    except Exception as e:
        print(f"An error occurred in the get_flicks function: {str(e)}")
        return 0, []


# main function to run the script and accept team IMDb IDs as a JSON string
def main():
    """Main function to run the script and process IMDb IDs passed as a JSON string."""
    
    # argument parser to accept the IMDb IDs array as a single JSON string
    parser = argparse.ArgumentParser(description="Fetch IMDb stunt credits for team members.")
    parser.add_argument('--team_ids', type=str, help='JSON array of IMDb IDs for team members', required=True)
    
    # parse arguments
    args = parser.parse_args()
    
    # parse the JSON string into a list of IMDb IDs
    try:
        team_ids = json.loads(args.team_ids)
        if not isinstance(team_ids, list):
            raise ValueError("The input must be a JSON array of IMDb IDs")
    
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {str(e)}")
        return

    # cll the get_flicks function with the parsed IMDb IDs
    total_credits, unique_films = get_flicks(team_ids)

    # Output the results in JSON format
    print(json.dumps({
        "total_credits": total_credits,
        "unique_films": unique_films
    }, indent=2))


# ensure the script can be executed directly
if __name__ == "__main__":
    main()
