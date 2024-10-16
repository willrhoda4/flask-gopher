




import re
import json
import time
import random
import argparse 
import requests
from   playwright.sync_api  import sync_playwright, TimeoutError
from   bs4                  import BeautifulSoup as bs







# Helper function to introduce delays (in milliseconds)
def sleep(ms):
    time.sleep(ms / 1000)


# Function to simulate random mouse movements across the screen
def random_mouse_move(page):
    for _ in range(10):  # Perform multiple random movements
        x = random.randint(0, 1366)
        y = random.randint(0, 768)
        page.mouse.move(x, y)
        sleep(random.randint(50, 300))  # Random delay between movementsfrom playwright.sync_api import sync_playwright



# Function to spoof navigator properties to avoid detection
def spoof_navigator(page):
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
        Object.defineProperty(navigator, 'userAgent', {
            get: () => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        });
        Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
    """)



# function to fetch stunt credits for a specific IMDb member
def fetch_stunt_credits(member):
    """Fetch stunt credits from an IMDb member's page.

    Args:
        member (str): IMDb ID of the member (e.g., 'nm1819605')

    Returns:
        list: List of HTML elements that contain stunt credits
    """

    args=  [
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--disable-extensions",
                "--no-first-run",
            ]
    
    with sync_playwright() as playwright:

        browser = playwright.chromium.launch(headless=False, args=args)
        context = browser.new_context(
            viewport=None,  # set viewport to None to make it look like a real user's window
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            geolocation={"longitude": 12.4924, "latitude": 41.8902},  # simulate real user location
            permissions=["geolocation"],  # grant permissions like a real user
            locale="en-US"
        )

        page = context.new_page()

        # use helper function to pass smell test for bot detection
        spoof_navigator(page)

        # construct the URL for the IMDb member's page
        url = f"https://www.imdb.com/name/{member}/?showAllCredits=true"

        # because IMDb page appears to never finish loading, we will not use wait_until
        # instead, we'll use a try-except block to force the script to continue 
        # after a delay determined by page.goto's timeout parameter
        try:
            print(f"navigating to imdb page for {member}...")
            page.goto(url, timeout=6000)

        except Exception as e:
            print(f"assuming the page is loaded and continuing...")


        # simulate random mouse movements
        random_mouse_move(page)

        # scroll down the page to ensure credits are loaded
        page.mouse.wheel(0, 2000)


        try:
            page.wait_for_selector("hgroup h3:has-text('Stunts')", timeout=90000)
            print("Stunts section loaded!")

            # extract stunt credit elements using the new structure
            li_elements = page.evaluate(
                """
                () => {
                    return Array.from(document.querySelectorAll("li[data-testid*='cred_stunts']")).map(li => li.outerHTML);
                }
                """
            )

            if li_elements:
                print(f"Found {len(li_elements)} stunt elements")
                return li_elements
            else:
                print("No elements found on the page.")
                return []

        except TimeoutError:
            print(f"Timeout occurred while waiting for stunts section on {url}")
            return []
        except Exception as e:
            print(f"An error occurred: {str(e)}")
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
        unique_films   = list(set(all_films))  # use set to remove duplicates
        total_credits  = len(all_films)

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



# # function to fetch stunt credits for a specific IMDb member
# def fetch_stunt_credits(member):
#     """Fetch stunt credits from an IMDb member's page.

#     Args:
#         member (str): IMDb ID of the member (e.g., 'nm1819605')

#     Returns:
#         list: List of HTML elements that contain stunt credits
#     """
#     with sync_playwright() as playwright:
#         # Launch browser in headless mode
#         browser = playwright.chromium.launch(headless=False)
#         context = browser.new_context(
#             user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#             viewport={"width": 1280, "height": 800},
#             locale="en-US",
#             extra_http_headers={
#                 "accept-language": "en-US,en;q=0.9",
#                 "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
#             }
#         )

#         page = context.new_page()
#         stealth(page)

#         url = f"https://www.imdb.com/name/{member}/?showAllCredits=true"

#         try:
#             # Open the IMDb page with extended timeout and network idle wait
#             page.goto(url, wait_until="networkidle", timeout=90000)
#             page.wait_for_timeout(5000)  # Wait an extra 5 seconds for everything to stabilize
#             print(f"Fetching credits for {member}...")

#             # Scroll through the page to trigger dynamic loading
#             page.mouse.wheel(0, 2000)
#             page.wait_for_timeout(2000)  # Give some time for scrolling to take effect

#             # Wait for the section with 'Stunts' text to load
#             page.wait_for_selector("hgroup h3:has-text('Stunts')", timeout=90000)
#             print("Stunts section loaded.")

#             # Extract <li> elements related to stunts
#             li_elements = page.evaluate(
#                 """
#                 () => {
#                     return Array.from(document.querySelectorAll("li[data-testid*='credit_stunts']")).map(li => li.outerHTML);
#                 }
#                 """
#             )

#             if li_elements:
#                 print(f"Found {len(li_elements)} stunt elements")
#                 return li_elements
#             else:
#                 print("No elements found on the page.")
#                 return []

#         except TimeoutError:
#             print(f"Timeout occurred while waiting for stunts section on {url}")
#             return []
#         except Exception as e:
#             print(f"An error occurred in the fetch_stunt_credits function: {str(e)}")
#             return []
#         finally:
#             browser.close()


