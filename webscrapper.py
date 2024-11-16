import requests
import pdfkit
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def get_rendered_html(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.get(url)
        time.sleep(5)
        html_content = driver.page_source
        return html_content
    finally:
        driver.quit()

def scrape_to_pdf(url, output_path):
    """Scrapes the given URL and saves the content to a PDF file."""
    
    config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
    
    options = {
        'enable-local-file-access': None,
        'no-stop-slow-scripts': None,
        'load-error-handling': 'ignore',
        'load-media-error-handling': 'ignore',
        'custom-header': [
            ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        ],
        'no-outline': None,
        'encoding': 'UTF-8',
        'javascript-delay': '1000',  # Đợi 1 giây cho JavaScript load
        'quiet': ''
    }

    try:
        # Sử dụng Selenium để lấy HTML đã render
        html_content = get_rendered_html(url)
        
        print(f"Content length: {len(html_content)}")
        print("Attempting to generate PDF...")
        
        pdfkit.from_string(html_content, output_path, configuration=config, options=options)
        print(f"Successfully saved PDF to: {output_path}")
    except Exception as e:
        print(f"Error generating PDF: {e}")

if __name__ == "__main__":
    url_to_scrape = "https://pattern-attraction-029.notion.site/JCL-13b8c254ba0b80e8be29d4949d9e6c38"
    output_pdf_path = "output.pdf"
    scrape_to_pdf(url_to_scrape, output_pdf_path)
