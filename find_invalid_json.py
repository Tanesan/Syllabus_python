import json
import os
import sys
from datetime import datetime

def find_invalid_json_files():
    """
    docs/all配下のJSONファイルをチェックして成績評価Gradingフィールドがないファイルを特定する
    """
    invalid_files = []
    total_files = 0
    
    for filename in os.listdir('docs/all'):
        if filename.endswith('.json'):
            total_files += 1
            file_path = os.path.join('docs/all', filename)
            
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                if '成績評価Grading1' not in data.get('評価', {}):
                    file_id = filename.replace('.json', '')
                    invalid_files.append(file_id)
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
    
    print(f"Found {len(invalid_files)} invalid files out of {total_files} total JSON files")
    return invalid_files

def main():
    invalid_files = find_invalid_json_files()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"invalid_files_{timestamp}.json"
    
    with open(result_file, 'w') as f:
        json.dump(invalid_files, f, ensure_ascii=False, indent=2)
    
    print(f"Invalid file IDs saved to {result_file}")
    
    if invalid_files:
        print("First 10 invalid files:")
        for i, file_id in enumerate(invalid_files[:10]):
            print(f"{i+1}. {file_id}")

if __name__ == "__main__":
    main()
