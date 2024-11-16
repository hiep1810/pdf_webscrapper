import requests
import pdfkit

def scrape_to_pdf(url, output_path):
    """Scrapes the given URL and saves the content to a PDF file."""

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        pdfkit.from_string(response.content, output_path)
        print(f"Successfully saved PDF to: {output_path}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
    except Exception as e:
        print(f"Error generating PDF: {e}")


if __name__ == "__main__":
    url_to_scrape = "https://www.example.com"  # Replace with the URL you want to scrape
    output_pdf_path = "output.pdf"
    scrape_to_pdf(url_to_scrape, output_pdf_path)
