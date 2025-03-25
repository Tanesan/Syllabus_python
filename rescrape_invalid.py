import json
import os
import sys
import time
import logging
from datetime import datetime
from define import act

logging.basicConfig(
    filename='rescrape_failures.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def rescrape_invalid_json(invalid_ids, max_retries=3):
    """
    無効なJSONファイルを再スクレイピングする関数
    
    Args:
        invalid_ids: 再スクレイピングするIDのリスト
        max_retries: 最大再試行回数
    """
    success_count = 0
    failure_count = 0
    
    for file_id in invalid_ids:
        print(f"Re-scraping {file_id}...")
        
        if len(file_id) >= 2:
            try:
                department_code = int(file_id[:2])
                subject_number = int(file_id[2:])
                
                success = False
                for attempt in range(max_retries):
                    print(f"Attempt {attempt+1}/{max_retries}")
                    success = act(department_code, subject_number, subject_number + 1)
                    if success:
                        print(f"Successfully re-scraped {file_id}")
                        success_count += 1
                        break
                    else:
                        print(f"Failed to re-scrape {file_id} (attempt {attempt+1}/{max_retries})")
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
        try:
            with open(sys.argv[1], 'r') as f:
                invalid_ids = json.load(f)
            print(f"Loaded {len(invalid_ids)} invalid IDs from {sys.argv[1]}")
        except Exception as e:
            print(f"Error loading file {sys.argv[1]}: {str(e)}")
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
        print(f"Check rescrape_failures.log for details on failed re-scraping attempts")

if __name__ == "__main__":
    main()
