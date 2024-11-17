import os
import json
import time
import base64
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def remove_whitespace(text):
    """Remove all spaces, newlines, and tabs from the given text."""
    return text.replace(" ", "").replace("\n", "").replace("\t", "")


def get_chrome_options():
    """Configure Chrome options for headless mode and PDF generation."""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Run Chrome in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Configure print-to-PDF preferences
    app_state = {
        "recentDestinations": [{"id": "Save as PDF", "origin": "local", "account": ""}],
        "selectedDestinationId": "Save as PDF",
        "version": 2,
    }

    profile = {
        "printing.print_preview_sticky_settings.appState": json.dumps(app_state),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
    }

    chrome_options.add_experimental_option("prefs", profile)
    return chrome_options


def initialize_driver(chrome_options):
    """Initialize and return the WebDriver."""
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("WebDriver initialized successfully.")
        return driver
    except Exception as e:
        logger.error(f"Error initializing WebDriver: {e}")
        raise


def clean_filename(filename):
    """Remove invalid characters from filename."""
    # List of invalid characters in filenames
    invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    
    # Replace invalid characters with underscores
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit the length of the filename (optional)
    max_length = 255  # Maximum filename length in most systems
    if len(filename) > max_length:
        filename = filename[:max_length]
    
    return filename


def generate_pdf(driver, url):
    """Generate a PDF from the given URL and save it to the specified path."""
    logger.info(f"Accessing webpage... {url}")
    driver.get(url)

    # Wait for the page to load completely
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".shadow-cursor-breadcrumb"))
    )

    logger.info("Generating PDF...")
    print_options = {
        "landscape": False,
        "displayHeaderFooter": False,
        "printBackground": True,
        "preferCSSPageSize": True,
    }

    try:
        result = driver.execute_cdp_cmd("Page.printToPDF", print_options)

        if "data" in result:
            logger.info("Processing PDF data...")
            pdf_data = result.get("data", "")
            clean_title = clean_filename(
                remove_whitespace(
                    driver.find_elements(
                        By.CSS_SELECTOR,
                        ".shadow-cursor-breadcrumb",
                    )[0].text
                ),
            )
            return base64.b64decode(pdf_data), clean_title

        else:
            logger.error("No data returned from PDF generation.")
            return None, None
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        return None, None


def save_pdf(pdf_data, output_directory, title):
    """Save the PDF data to a file."""
    if pdf_data:
        try:
            file_path = os.path.join(output_directory, f"{title}.pdf")
            with open(file_path, "wb") as f:
                f.write(pdf_data)
            logger.info(f"PDF saved to: {file_path}")
        except Exception as e:
            logger.error(f"Error saving PDF: {e}")
    else:
        logger.error("No PDF data to save.")


def scrape_to_pdf(url, output_directory, driver=None):
    """Main function to scrape the webpage and save it as a PDF."""
    try:
        pdf_data, title = generate_pdf(driver, url)
        save_pdf(pdf_data, output_directory, title)

    except Exception as e:
        logger.error(f"Scraping failed: {e}")


def get_all_page_links(url, driver):
    """Get all the links on the page."""
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-block-id] a"))
    )
    return [
        tag.get_attribute("href")
        for tag in driver.find_elements(By.CSS_SELECTOR, "div[data-block-id] a")
    ]


def recursive_scrape(url, output_directory, visited_links, driver):
    """Recursively scrape a URL and its links to save PDFs."""
    if url in visited_links:
        return
    visited_links.add(url)

    # Scrape and save the PDF
    scrape_to_pdf(url, output_directory, driver)

    # Get all the links on the page and recursively scrape them
    try:
        links = get_all_page_links(url, driver)
        for link in links:
            recursive_scrape(link, output_directory, visited_links, driver)
    except Exception as e:
        logger.error(f"Error during recursive scrape of {url}: {e}")


if __name__ == "__main__":
    # Get the current directory
    current_directory = os.getcwd()
    output_pdf_directory = os.path.join(current_directory, "pdf")

    if not os.path.exists(output_pdf_directory):
        os.makedirs(output_pdf_directory)


    url_to_scrape = "https://pattern-attraction-029.notion.site/TSO-ISPF-Course-1358c254ba0b807a9eefdb0421361218"

    # Initialize the WebDriver once
    chrome_options = get_chrome_options()
    driver = initialize_driver(chrome_options)

    # Initialize visited links set
    visited_links = set()
    try:
        recursive_scrape(url_to_scrape, output_pdf_directory, visited_links, driver)
    finally:
        driver.quit()  # Make sure to quit the driver at the end
