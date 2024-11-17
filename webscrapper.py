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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def replace_slash(text):
    """Replace all slashes with a underscore."""
    return text.replace("/", "_")

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
        'recentDestinations': [{
            'id': 'Save as PDF',
            'origin': 'local',
            'account': ''
        }],
        'selectedDestinationId': 'Save as PDF',
        'version': 2
    }

    profile = {
        'printing.print_preview_sticky_settings.appState': json.dumps(app_state),
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'plugins.always_open_pdf_externally': True
    }
    
    chrome_options.add_experimental_option('prefs', profile)
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


def generate_pdf(driver, url):
    """Generate a PDF from the given URL and save it to the specified path."""
    logger.info("Accessing webpage...")
    driver.get(url)
    time.sleep(5)  # Allow time for the page to load

    logger.info("Generating PDF...")
    print_options = {
        'landscape': False,
        'displayHeaderFooter': False,
        'printBackground': True,
        'preferCSSPageSize': True,
    }

    try:
        result = driver.execute_cdp_cmd('Page.printToPDF', print_options)

        if 'data' in result:
            logger.info("Processing PDF data...")
            pdf_data = result.get('data', '')
            return base64.b64decode(pdf_data), replace_slash(remove_whitespace(driver.find_elements(By.CSS_SELECTOR, '.shadow-cursor-breadcrumb')[0].text))

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
            with open(os.path.join(output_directory, f"{title}.pdf"), 'wb') as f:
                f.write(pdf_data)
            logger.info(f"PDF saved to: {os.path.join(output_directory, f'{title}.pdf')}")
        except Exception as e:
            logger.error(f"Error saving PDF: {e}")
    else:
        logger.error("No PDF data to save.")


def scrape_to_pdf(url, output_directory):
    """Main function to scrape the webpage and save it as a PDF."""    
    chrome_options = get_chrome_options()
    
    try:
        driver = initialize_driver(chrome_options)
        
        pdf_data, title = generate_pdf(driver, url)
        save_pdf(pdf_data, output_directory, title)

    except Exception as e:
        logger.error(f"Scraping failed: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()


def get_all_page_links(url):
    """Get all the links on the page."""
    chrome_options = get_chrome_options()
    driver = initialize_driver(chrome_options)
    driver.get(url)
    time.sleep(5)
    return [tag.get_attribute('href') for tag in driver.find_elements(By.CSS_SELECTOR, 'div[data-block-id] a')]



def recursive_scrape(url, output_directory):
    """Recursive function to scrape all the pages and save them as PDFs."""
    logger.info(f"Scraping {url}...")
    scrape_to_pdf(url, output_directory)
    links = get_all_page_links(url)
    logger.info(f"Found {len(links)} links on the page.")
    for link in links:
        recursive_scrape(link, output_directory)

if __name__ == "__main__":
    # Use the current working directory to save the PDF
    current_directory = os.getcwd()
    output_pdf_directory = os.path.join(current_directory, 'pdf')

    url_to_scrape = "https://pattern-attraction-029.notion.site/JCL-13b8c254ba0b80e8be29d4949d9e6c38"
    
    recursive_scrape(url_to_scrape, output_pdf_directory)
