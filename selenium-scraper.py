from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Setup fast, headless Chrome
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.page_load_strategy = 'eager'  # Don't wait for full page load

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Load the page
url = "https://www.uniqlo.com/jp/ja/search?q=474479"
driver.get(url)

# Wait just for <link> tags to appear
WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.TAG_NAME, "link"))
)

# Extract only the image preload <link>
image_url = None
for link in driver.find_elements(By.TAG_NAME, "link"):
    if link.get_attribute("as") == "image" and link.get_attribute("rel") == "preload":
        image_url = link.get_attribute("href")
        break

driver.quit()

# Output
if image_url:
    print("Image URL:", image_url)
else:
    print("No image preload <link> found.")
