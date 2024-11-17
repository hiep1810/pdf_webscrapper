from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
# Start a WebDriver session (using Chrome in this case)
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Navigate to the desired webpage
try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    print("Đang truy cập trang web...")
    driver.get("https://pattern-attraction-029.notion.site/JCL-13b8c254ba0b80e8be29d4949d9e6c38")
    time.sleep(5)
    # Find all divs with the data-block-id attribute
    divs = driver.find_elements(By.CSS_SELECTOR, 'div[data-block-id]')

    # Iterate over each div and check if it contains a specific tag (e.g., <p>)
    count = 0
    for div in divs:
        # Check if the div contains any <p> tags inside it
        inner_elements = div.find_elements(By.TAG_NAME, 'a')  # Change 'p' to any tag you're interested in
        if inner_elements:
            print(f"Div with data-block-id='{div.get_attribute('data-block-id')}' contains <a> tags")
            count += 1
        else:
            print(f"Div with data-block-id='{div.get_attribute('data-block-id')}' does NOT contain <a> tags")

    print(f"Total divs with <a> tags: {count}")
    # Close the browser when done
    driver.quit()
except Exception as e:
    print(f"Lỗi xảy ra: {e}")

