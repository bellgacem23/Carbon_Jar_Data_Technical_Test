from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging

logging.basicConfig(level=logging.INFO)

def get_shadow_root(driver, element):
    """Récupère le Shadow Root d'un élément de manière robuste"""
    try:
        if element is None:
            raise ValueError("L'élément Shadow Host est null")
        
        shadow_root = driver.execute_script('return arguments[0].shadowRoot', element)
        if shadow_root is None:
            raise Exception("Shadow Root non trouvé pour l'élément")
        
        return shadow_root
    except Exception as e:
        logging.error(f"Échec récupération Shadow Root: {e}")
        raise

def scrape_french_portal(url="http://hypothetical-french-gov-portal.fr/factors"):
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        
        year_select = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'yearSelect'))
        )
        year_select.click()
        
        year_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//option[@value='2024']"))
        )
        year_option.click()
        
        load_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'loadDataBtn'))
        )
        load_button.click()
        
        table = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, 'resultsTable'))
        )
        
        # We wait for table to have some rows
        WebDriverWait(driver, 10).until(
            lambda driver: len(table.find_elements(By.TAG_NAME, 'tr')) > 1
        )
        
        rows = table.find_elements(By.TAG_NAME, 'tr')[1:]
        data = []
        for i, row in enumerate(rows):
            cols = row.find_elements(By.TAG_NAME, 'td')
            if len(cols) < 3:
                logging.warning(f"Row {i} doesn't have enough columns, skipping")
                continue
                
            shadow_host = WebDriverWait(row, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'factor-component'))
            )
            
            shadow_content = get_shadow_root(driver, shadow_host)
            
            factor_value_element = WebDriverWait(shadow_content, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.factor-val'))
            )
            factor_value = factor_value_element.text
            
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