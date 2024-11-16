from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import json
import base64

def scrape_to_pdf(url, output_path):
    """Scrapes the given URL and saves the content to a PDF file."""
    output_path = os.path.abspath(output_path)
    output_dir = os.path.dirname(output_path)
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    appState = {
        'recentDestinations': [{
            'id': 'Save as PDF',
            'origin': 'local',
            'account': ''
        }],
        'selectedDestinationId': 'Save as PDF',
        'version': 2
    }

    profile = {
        'printing.print_preview_sticky_settings.appState': json.dumps(appState),
        'savefile.default_directory': output_dir,
        'download.default_directory': output_dir,
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'plugins.always_open_pdf_externally': True
    }
    
    chrome_options.add_experimental_option('prefs', profile)
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("Đang truy cập trang web...")
        driver.get(url)
        time.sleep(5)
        
        print("Đang tạo PDF...")
        print_options = {
            'landscape': False,
            'displayHeaderFooter': False,
            'printBackground': True,
            'preferCSSPageSize': True,
            'path': output_path
        }
        
        result = driver.execute_cdp_cmd('Page.printToPDF', print_options)
        
        if 'data' in result:
            print("Đang xử lý dữ liệu PDF...")
            pdf_data = result.get('data', '')
            try:
                pdf_bytes = base64.b64decode(pdf_data)
                with open(output_path, 'wb') as f:
                    f.write(pdf_bytes)
                print(f"PDF đã được lưu tại: {output_path}")
            except Exception as e:
                print(f"Lỗi khi xử lý PDF: {str(e)}")
                print(f"Độ dài dữ liệu PDF: {len(pdf_data)}")
                print(f"Vài ký tự đầu tiên: {pdf_data[:100]}")
        else:
            print("Không thể tạo PDF: Không có dữ liệu trả về")
            
    except Exception as e:
        print(f"Lỗi: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    # Use the current working directory for saving the PDF
    output_pdf_path = os.path.join(os.getcwd(), "notion_output.pdf")

    url_to_scrape = "https://pattern-attraction-029.notion.site/JCL-13b8c254ba0b80e8be29d4949d9e6c38"
    scrape_to_pdf(url_to_scrape, output_pdf_path)