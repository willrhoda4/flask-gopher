import re
import json
import requests
from flask import request, jsonify
from bs4 import BeautifulSoup as bs
from playwright.sync_api import sync_playwright


def fetch_stunt_credits(member):

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )
        page = context.new_page()

        url = f"https://www.imdb.com/name/{member}/?showAllCredits=true"
        page.goto(url)

        print(f"Fetching credits for {member}...")

        try:
            # Wait for the <h3> element that contains the "Stunts" text
            page.wait_for_selector("hgroup h3:has-text('Stunts')", timeout=60000)
            print("Stunts section loaded.")

            page.wait_for_timeout(2000)  # Manual delay to ensure page is fully loaded

            # Now wait for the <li> elements to appear
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
                return []

        except Exception as e:
            print(f"An error occurred in the fetch_stunt_credits function: {str(e)}")
            return []

        finally:
            browser.close()


def get_flicks():
    try:
        data = request.json
        team = data.get("team") or []
        all_films = []

        print(f"Team list received: {team}")

        for member in team:
            stunt_elements = fetch_stunt_credits(member)
            print(f"Processing {len(stunt_elements)} stunt elements for {member}")

            # Extracting film IDs from the li elements
            film_ids = [re.search(r"tt\d+", li).group() for li in stunt_elements]
            # print(f"Film IDs extracted: {film_ids}")
            all_films += film_ids

        total_credits = len(all_films)
        unique_films = list(set(all_films))

        print(f"Total Credits: {total_credits}")

        return jsonify([total_credits, unique_films])

    except Exception as e:
        print(f"An error occurred in the getFlicks function: {str(e)}")
        return f"An error occurred in the getFlicks function: {str(e)}", 500
