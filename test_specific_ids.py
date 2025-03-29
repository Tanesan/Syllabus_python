import os
import sys
import json
import logging
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException, TimeoutException, NoSuchElementException

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from define import handle_alert, safe_click

log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_problematic_ids.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def test_specific_id(file_id, max_retries=3):
    """
    特定のIDをテストする関数
    
    Args:
        file_id: テストするID
        max_retries: 最大再試行回数
        
    Returns:
        bool: 成功した場合はTrue、失敗した場合はFalse
    """
    logging.info(f"Testing ID: {file_id}")
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    for attempt in range(max_retries):
        logging.info(f"Attempt {attempt+1}/{max_retries}")
        
        try:
            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(30)
            
            driver.get('https://syllabus.kwansei.ac.jp/uniasv2/UnSSOLoginControlFree')
            logging.info("Accessed login page")
            
            select_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'selLsnMngPostCd'))
            )
            from selenium.webdriver.support.ui import Select
            select_object = Select(select_element)
            select_object.select_by_index(1)
            select_object.select_by_value("21")  # 神学部
            logging.info("Selected department")
            
            year_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'txtLsnOpcFcy'))
            )
            year_input.clear()
            year_input.send_keys("2025")
            logging.info("Set year to 2025")
            
            if not safe_click(driver, By.NAME, 'ESearch', timeout=10):
                logging.error("Failed to click search button")
                driver.quit()
                continue
            
            logging.info("Clicked search button")
            
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'tblBdr'))
            )
            logging.info("Search results loaded")
            
            id_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'txtKmkId'))
            )
            id_input.clear()
            id_input.send_keys(file_id)
            logging.info(f"Entered ID: {file_id}")
            
            if not safe_click(driver, By.NAME, 'ESearch', timeout=10):
                logging.error("Failed to click search button for ID search")
                driver.quit()
                continue
                
            logging.info("Clicked search button for ID search")
            
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'tblBdr'))
                )
                logging.info("ID search results loaded")
            except TimeoutException:
                logging.error("Timeout waiting for ID search results")
                driver.quit()
                continue
            
            try:
                refer_elements = driver.find_elements_by_name('ERefer')
                if len(refer_elements) == 0:
                    logging.warning("No ERefer elements found")
                    driver.quit()
                    continue
                
                if not safe_click(driver, By.NAME, 'ERefer', timeout=10):
                    logging.error("Failed to click ERefer element")
                    try:
                        driver.execute_script("arguments[0].click();", refer_elements[0])
                        logging.info("Clicked ERefer element using JavaScript")
                    except Exception as js_e:
                        logging.error(f"JavaScript click also failed: {str(js_e)}")
                        driver.quit()
                        continue
                
                logging.info("Clicked ERefer element")
                
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'tblBdr'))
                )
                logging.info("Detail page loaded")
                
                if handle_alert(driver):
                    logging.info("Alert handled successfully")
                
                screenshot_path = f"test_{file_id}_screenshot.png"
                driver.save_screenshot(screenshot_path)
                logging.info(f"Screenshot saved to {screenshot_path}")
                
                logging.info(f"Successfully accessed details for ID: {file_id}")
                driver.quit()
                return True
                
            except UnexpectedAlertPresentException:
                logging.warning("Alert encountered during ERefer click")
                if not handle_alert(driver):
                    logging.error("Failed to handle alert")
                    driver.quit()
                    continue
                
                try:
                    refer_elements = driver.find_elements_by_name('ERefer')
                    if len(refer_elements) > 0:
                        if not safe_click(driver, By.NAME, 'ERefer', timeout=5):
                            driver.execute_script("arguments[0].click();", refer_elements[0])
                    else:
                        logging.warning("No ERefer elements found after handling alert")
                        driver.quit()
                        continue
                except Exception as e:
                    logging.error(f"Error after handling alert: {str(e)}")
                    driver.quit()
                    continue
                
            except IndexError:
                logging.error("IndexError: list index out of range encountered")
                driver.quit()
                continue
                
            except Exception as e:
                logging.error(f"Unexpected error during element interaction: {str(e)}")
                driver.quit()
                continue
                
        except Exception as e:
            logging.error(f"Error testing ID {file_id}: {str(e)}")
            if 'driver' in locals():
                driver.quit()
            
            if attempt < max_retries - 1:
                logging.info(f"Retrying in 5 seconds...")
                time.sleep(5)
            else:
                logging.error(f"Failed to test ID {file_id} after {max_retries} attempts")
                return False
    
    return False

def main():
    """メイン関数"""
    test_ids = ["25050119", "26459004"]
    
    results = {}
    
    for file_id in test_ids:
        logging.info(f"=== Testing ID: {file_id} ===")
        success = test_specific_id(file_id)
        results[file_id] = "Success" if success else "Failed"
        logging.info(f"Result for ID {file_id}: {results[file_id]}")
        logging.info("=" * 50)
    
    logging.info("\nTest Results Summary:")
    for file_id, result in results.items():
        logging.info(f"ID {file_id}: {result}")
    
    with open('test_specific_ids_simple.log', 'w') as f:
        f.write(f"Test run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("Test Results Summary:\n")
        for file_id, result in results.items():
            f.write(f"ID {file_id}: {result}\n")

if __name__ == "__main__":
    main()
