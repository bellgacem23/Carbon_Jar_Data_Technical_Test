from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, logging

logging.basicConfig(level=logging.INFO)

def get_shadow_root(driver, element):
    return driver.execute_script('return arguments[0].shadowRoot', element)

def scrape_french_portal(url="http://hypothetical-french-gov-portal.fr/factors"):
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        driver.find_element(By.ID, 'yearSelect').click()
        driver.find_element(By.XPATH, "//option[@value='2024']").click()
        driver.find_element(By.ID, 'loadDataBtn').click()
        time.sleep(5) # <<< PROBLEM 1: Brittle Wait
        table = driver.find_element(By.ID, 'resultsTable') # <<< PROBLEM 2: Often Fails
        rows = table.find_elements(By.TAG_NAME, 'tr')[1:]
        data = []
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, 'td')
            shadow_host = cols[2].find_element(By.TAG_NAME, 'factor-component')
            shadow_content = get_shadow_root(driver, shadow_host) # <<< PROBLEM 3: Might be null/wrong
            factor_value = shadow_content.find_element(By.CSS_SELECTOR, '.factor-val').text
            data.append({'Sector': cols[0].text, 'Factor': factor_value})
        return data
    except Exception as e:
        logging.error(f"Scraping failed: {e}", exc_info=True)
        return None
    finally:
        driver.quit()
        
if __name__ == "__main__":
    results = scrape_french_portal()
    if results:
        for item in results:
            print(item)