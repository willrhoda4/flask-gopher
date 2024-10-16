





from playwright.sync_api import sync_playwright
import random
import time



# Helper function to introduce delays (in milliseconds)
def sleep(ms):
    time.sleep(ms / 1000)



# Function to simulate random mouse movements across the screen
def random_mouse_move(page):
    for _ in range(10):  # Perform multiple random movements
        x = random.randint(0, 1366)
        y = random.randint(0, 768)
        page.mouse.move(x, y)
        sleep(random.randint(50, 300))  # Random delay between movements



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



# Main function to test stealth mode on bot.sannysoft.com
def stealth_test():
    """Endpoint to test stealth mode on bot.sannysoft.com."""
    with sync_playwright() as p:
        # Launch the browser with some additional flags to avoid detection
        browser = p.chromium.launch(
            headless=False,  # Set to True for production to avoid opening the browser window
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--disable-extensions",
                "--no-first-run",
            ]
        )
        
        # Create a new browser context
        context = browser.new_context(
            viewport=None,  # Set viewport to None to make it look like a real user's window
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            geolocation={"longitude": 12.4924, "latitude": 41.8902},  # Simulate real user location
            permissions=["geolocation"],  # Grant permissions like a real user
            locale="en-US"
        )
        
        # Open a new page in the browser
        page = context.new_page()
        
        # Spoof browser properties to avoid bot detection
        spoof_navigator(page)

        print("I can print")
        
         # Navigate to IMDb member's credits page
        url = f"https://www.imdb.com/name/nm1819605/?showAllCredits=true"
        # page.goto(url, wait_until="load", timeout=90000)

             # because IMDb page appears to never finish loading, we will not use wait_until
        # instead, we'll use a try-except block to force the script to continue 
        # after a delay determined by page.goto's timeout parameter
        try:
            print(f"navigating to imdb page...")
            page.goto(url, timeout=3000)

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

