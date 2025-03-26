import sys
import json
import os
from rescrape_invalid import rescrape_invalid_json

def main():
    """
    アラート処理機能をテストする
    """
    print("Testing alert handling functionality...")
    
    test_ids = ["26459008", "26459018", "23065814"]
    
    print(f"Testing with IDs: {', '.join(test_ids)}")
    
    success_count, failure_count = rescrape_invalid_json(test_ids, max_retries=2)
    
    print(f"\nTest completed:")
    print(f"- Successfully re-scraped: {success_count}")
    print(f"- Failed to re-scrape: {failure_count}")
    
    if os.path.exists('rescrape_failures.log'):
        print("\nLog file content:")
        with open('rescrape_failures.log', 'r') as f:
            print(f.read())

if __name__ == "__main__":
    main()
