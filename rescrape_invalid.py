import json
import os
import sys
import time
import logging
import re
from datetime import datetime
from define import act
from selenium.common.exceptions import UnexpectedAlertPresentException

log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rescrape_failures.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def is_valid_id(file_id):
    """
    ファイルIDが有効な形式かどうかを検証する
    
    Args:
        file_id: 検証するID
    
    Returns:
        bool: IDが有効な形式の場合はTrue、そうでない場合はFalse
    """
    return bool(re.match(r'^\d{2,}$', file_id))

def rescrape_invalid_json(invalid_ids, max_retries=3):
    """
    無効なJSONファイルを再スクレイピングする関数
    
    Args:
        invalid_ids: 再スクレイピングするIDのリスト
        max_retries: 最大再試行回数
    
    Returns:
        tuple: (成功数, 失敗数)
    """
    success_count = 0
    failure_count = 0
    
    for file_id in invalid_ids:
        if not isinstance(file_id, str):
            file_id = str(file_id)
        
        file_id = file_id.strip()
        print(f"Re-scraping {file_id}...")
        
        if is_valid_id(file_id):
            try:
                department_code = int(file_id[:2])
                subject_number = int(file_id[2:])
                
                if department_code <= 0 or subject_number <= 0:
                    raise ValueError("Invalid department code or subject number")
                
                success = False
                for attempt in range(max_retries):
                    print(f"Attempt {attempt+1}/{max_retries}")
                    try:
                        success = act(department_code, subject_number, subject_number + 1)
                        if success:
                            print(f"Successfully re-scraped {file_id}")
                            success_count += 1
                            break
                        else:
                            print(f"Failed to re-scrape {file_id} (attempt {attempt+1}/{max_retries})")
                            if attempt < max_retries - 1:
                                time.sleep(5)
                    except UnexpectedAlertPresentException as e:
                        print(f"Alert encountered during scraping: {str(e)}")
                        logging.warning(f"Alert encountered for {file_id}: {str(e)}")
                        if attempt < max_retries - 1:
                            time.sleep(5)
                
                if not success:
                    failure_count += 1
                    logging.warning(f"Failed to re-scrape {file_id} after {max_retries} attempts")
            except Exception as e:
                failure_count += 1
                error_message = f"Error re-scraping {file_id}: {str(e)}"
                print(error_message)
                logging.error(error_message)
        else:
            failure_count += 1
            error_message = f"Invalid ID format: {file_id}"
            print(error_message)
            logging.error(error_message)
    
    return success_count, failure_count

def main():
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        
        if not os.path.exists(input_file):
            print(f"Error: File {input_file} does not exist")
            return
        
        try:
            with open(input_file, 'r') as f:
                invalid_ids = json.load(f)
                
            if not isinstance(invalid_ids, list):
                print("Error: Input file must contain a JSON array of IDs")
                return
                
            print(f"Loaded {len(invalid_ids)} invalid IDs from {input_file}")
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON format in {input_file}: {str(e)}")
            return
        except Exception as e:
            print(f"Error loading file {input_file}: {str(e)}")
            return
    else:
        print("Usage: python rescrape_invalid.py <invalid_ids_file.json>")
        print("Please provide a JSON file containing the list of invalid IDs")
        return
    
    print(f"Starting re-scraping of {len(invalid_ids)} invalid files...")
    success_count, failure_count = rescrape_invalid_json(invalid_ids)
    
    print(f"\nRe-scraping completed:")
    print(f"- Successfully re-scraped: {success_count}")
    print(f"- Failed to re-scrape: {failure_count}")
    
    if failure_count > 0:
        print(f"Check {log_file} for details on failed re-scraping attempts")

if __name__ == "__main__":
    main()
