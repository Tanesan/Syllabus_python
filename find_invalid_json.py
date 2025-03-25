import json
import os
import sys
import re
from datetime import datetime

def is_valid_json_filename(filename):
    """
    JSONファイル名が有効かどうかを検証する
    
    Args:
        filename: 検証するファイル名
    
    Returns:
        bool: ファイル名が有効な場合はTrue、そうでない場合はFalse
    """
    return bool(re.match(r'^[\w\-\.]+\.json$', filename))

def find_invalid_json_files():
    """
    docs/all配下のJSONファイルをチェックして成績評価Gradingフィールドがないファイルを特定する
    """
    invalid_files = []
    total_files = 0
    
    docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs', 'all')
    
    if not os.path.exists(docs_dir) or not os.path.isdir(docs_dir):
        print(f"Error: Directory {docs_dir} does not exist or is not a directory")
        return []
    
    for filename in os.listdir(docs_dir):
        if filename.endswith('.json') and is_valid_json_filename(filename):
            total_files += 1
            file_path = os.path.join(docs_dir, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if not isinstance(data, dict):
                    print(f"Warning: {filename} does not contain a valid JSON object")
                    continue
                
                if '成績評価Grading1' not in data.get('評価', {}):
                    file_id = filename.replace('.json', '')
                    if re.match(r'^\d+$', file_id):
                        invalid_files.append(file_id)
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON format in {filename}: {str(e)}")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
    
    print(f"Found {len(invalid_files)} invalid files out of {total_files} total JSON files")
    return invalid_files

def main():
    invalid_files = find_invalid_json_files()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"invalid_files_{timestamp}.json"
    
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(output_dir, result_file)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(invalid_files, f, ensure_ascii=False, indent=2)
        
        print(f"Invalid file IDs saved to {result_file}")
        
        if invalid_files:
            print("First 10 invalid files:")
            for i, file_id in enumerate(invalid_files[:10]):
                print(f"{i+1}. {file_id}")
    except Exception as e:
        print(f"Error saving results to {result_file}: {str(e)}")

if __name__ == "__main__":
    main()
