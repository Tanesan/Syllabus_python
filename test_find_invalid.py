import json
import os
from find_invalid_json import find_invalid_json_files

def main():
    """
    find_invalid_json.pyの機能をテストする
    """
    print("Testing find_invalid_json.py functionality...")
    
    invalid_files = find_invalid_json_files()
    
    print(f"Found {len(invalid_files)} invalid files")
    
    if invalid_files:
        print("First 10 invalid files:")
        for i, file_id in enumerate(invalid_files[:10]):
            print(f"{i+1}. {file_id}")
    
    test_file = "test_invalid.json"
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(invalid_files[:5], f, ensure_ascii=False, indent=2)
    
    print(f"Created test file with 5 invalid IDs: {test_file}")
    print(f"You can now run: python rescrape_invalid.py {test_file}")

if __name__ == "__main__":
    main()
