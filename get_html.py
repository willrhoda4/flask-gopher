from playwright.sync_api import sync_playwright


def run():
    with sync_playwright() as playwright:
        # Set up the browser and context
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )

        # Open a new page within the context
        page = context.new_page()

        url = "https://www.imdb.com/name/nm0804055/?showAllCredits=true"
        page.goto(url)

        print("Waiting for the Stunts section to load...")

        try:
            # Wait for the <h3> element that contains the "Stunts" text
            page.wait_for_selector("hgroup h3:has-text('Stunts')", timeout=60000)
            print("Stunts section loaded.")

            page.wait_for_timeout(2000)  # 1000 milliseconds = 1 second

            # Now wait for the <li> elements to appear
            li_elements = page.wait_for_selector(
                "li[data-testid*='credit_stunts']", timeout=60000
            )
            print("Stunt credits found.")

            # Extract the elements directly via JavaScript execution
            li_elements = page.evaluate(
                """
            () => {
                return Array.from(document.querySelectorAll("li[data-testid*='credit_stunts']")).map(li => li.outerHTML);
            }
            """
            )

            if li_elements:
                print(f"Found {len(li_elements)} stunt elements")
                # print(li_elements[:5])  # Print first 5 elements for verification
            else:
                print("No elements found on the page.")

        except Exception as e:
            print(f"An error occurred in the run function: {str(e)}")

        finally:
            # Close the browser after the operation is complete
            browser.close()


if __name__ == "__main__":
    run()
