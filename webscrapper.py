import requests
import pdfkit

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
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        
        html_content = response.content.decode('utf-8')
        
        print(f"Content length: {len(html_content)}")
        print("Attempting to generate PDF...")
        
        pdfkit.from_string(html_content, output_path, configuration=config, options=options)
        print(f"Successfully saved PDF to: {output_path}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
    except Exception as e:
        print(f"Error generating PDF: {e}")

if __name__ == "__main__":
    url_to_scrape = "https://pattern-attraction-029.notion.site/JCL-13b8c254ba0b80e8be29d4949d9e6c38"
    output_pdf_path = "output.pdf"
    scrape_to_pdf(url_to_scrape, output_pdf_path)
