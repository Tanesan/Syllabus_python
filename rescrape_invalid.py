import json
import os
import sys
import time
import logging
import re
import argparse
from datetime import datetime
from define import act
from selenium.common.exceptions import UnexpectedAlertPresentException

log_dir = os.path.dirname(os.path.abspath(__file__))
failure_log = os.path.join(log_dir, 'rescrape_failures.log')
detailed_log = os.path.join(log_dir, 'rescrape_detailed.log')

def setup_logging():
    """詳細なロギング設定を行う関数"""
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(detailed_log),
            logging.FileHandler(failure_log),
            logging.StreamHandler()
        ]
    )
    
    logging.info("Logging initialized with both file and console output")

setup_logging()

def is_valid_id(file_id):
    """
    ファイルIDが有効な形式かどうかを検証する
    
    Args:
        file_id: 検証するID
    
    Returns:
        bool: IDが有効な形式の場合はTrue、そうでない場合はFalse
    """
    return bool(re.match(r'^\d{2,}$', file_id))

def save_progress(processed_ids, output_file):
    """
    処理済みIDをファイルに保存する
    
    Args:
        processed_ids: 処理済みIDのリスト
        output_file: 出力ファイルパス
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_ids, f, ensure_ascii=False, indent=2)
    print(f"Progress saved to {output_file}")

def load_progress(progress_file):
    """
    進捗ファイルから処理済みIDを読み込む
    
    Args:
        progress_file: 進捗ファイルパス
        
    Returns:
        list: 処理済みIDのリスト
    """
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading progress file: {str(e)}")
            return []
    return []

def rescrape_invalid_json(invalid_ids, max_retries=3, batch_size=50, batch_index=0, total_batches=1, progress_file=None, max_items=30):
    """
    無効なJSONファイルを再スクレイピングする関数
    
    Args:
        invalid_ids: 再スクレイピングするIDのリスト
        max_retries: 最大再試行回数
        batch_size: バッチサイズ（指定された場合）
        batch_index: 処理するバッチのインデックス（0から始まる）
        total_batches: 合計バッチ数
        progress_file: 進捗を保存するファイル
        max_items: 処理する最大アイテム数
        
    Returns:
        tuple: (成功数, 失敗数)
    """
    success_count = 0
    failure_count = 0
    processed_ids = []
    item_count = 0  # 処理したアイテムの数をカウント
    
    if progress_file and os.path.exists(progress_file):
        processed_ids = load_progress(progress_file)
        print(f"Loaded {len(processed_ids)} already processed IDs from {progress_file}")
    
    if total_batches > 1:
        batch_size = len(invalid_ids) // total_batches + (1 if len(invalid_ids) % total_batches > 0 else 0)
        start_idx = batch_index * batch_size
        end_idx = min(start_idx + batch_size, len(invalid_ids))
        target_ids = invalid_ids[start_idx:end_idx]
        print(f"Processing batch {batch_index+1}/{total_batches}: IDs {start_idx} to {end_idx-1} ({len(target_ids)} IDs)")
    else:
        target_ids = invalid_ids
    
    target_ids = [id for id in target_ids if id not in processed_ids]
    print(f"After removing already processed IDs: {len(target_ids)} IDs to process")
    
    for i in range(0, len(target_ids), batch_size):
        current_batch = target_ids[i:i+batch_size]
        print(f"Processing mini-batch {i//batch_size + 1}/{(len(target_ids) + batch_size - 1)//batch_size}: {len(current_batch)} IDs")
        
        for file_id in current_batch:
            if not isinstance(file_id, str):
                file_id = str(file_id)
            print(f"now item is {item_count}")
            if item_count >= max_items:
                print(f"Reached maximum number of items to process ({max_items}). Stopping.")
                break
                
            file_id = file_id.strip()
            print(f"Re-scraping {file_id}...")
            
            item_count += 1
            
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
                        except IndexError as e:
                            print(f"Index error while scraping {file_id}: {str(e)}")
                            logging.error(f"Index error for {file_id}: {str(e)}")
                            break  # インデックスエラーは再試行しても解決しないため中断
                        except Exception as e:
                            print(f"Error re-scraping {file_id}: {str(e)}")
                            logging.error(f"Error for {file_id}: {str(e)}")
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
            
            processed_ids.append(file_id)
            
            if progress_file and len(processed_ids) % 10 == 0:
                save_progress(processed_ids, progress_file)
        
        if progress_file:
            save_progress(processed_ids, progress_file)
    
    return success_count, failure_count

def main():
    parser = argparse.ArgumentParser(description='無効なJSONファイルを再スクレイピングするスクリプト')
    parser.add_argument('input_file', help='無効なIDのリストを含むJSONファイル')
    parser.add_argument('--batch', type=int, default=0, help='処理するバッチのインデックス（0から始まる）')
    parser.add_argument('--total-batches', type=int, default=1, help='合計バッチ数')
    parser.add_argument('--batch-size', type=int, default=50, help='ミニバッチサイズ')
    parser.add_argument('--max-retries', type=int, default=3, help='スクレイピングの最大再試行回数')
    parser.add_argument('--ids', help='カンマ区切りの特定IDリスト（テスト用）')
    
    args = parser.parse_args()
    
    input_file = args.input_file
    
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} does not exist")
        return
    
    if args.ids:
        invalid_ids = args.ids.split(',')
        logging.info(f"Using specific IDs for testing: {invalid_ids}")
    else:
        try:
            with open(input_file, 'r') as f:
                invalid_ids = json.load(f)
                
            if not isinstance(invalid_ids, list):
                logging.error("Error: Input file must contain a JSON array of IDs")
                return
                
            logging.info(f"Loaded {len(invalid_ids)} invalid IDs from {input_file}")
        except json.JSONDecodeError as e:
            logging.error(f"Error: Invalid JSON format in {input_file}: {str(e)}")
            return
        except Exception as e:
            logging.error(f"Error loading file {input_file}: {str(e)}")
            return
    
    progress_file = f"rescrape_progress_batch{args.batch}.json"
    
    logging.info(f"Starting re-scraping of invalid files (Batch {args.batch+1}/{args.total_batches})...")
    success_count, failure_count = rescrape_invalid_json(
        invalid_ids, 
        max_retries=args.max_retries,
        batch_size=args.batch_size,
        batch_index=args.batch,
        total_batches=args.total_batches,
        progress_file=progress_file,
        max_items=30  # 最大30件のアイテムのみ処理
    )
    
    summary = f"\nRe-scraping completed for batch {args.batch+1}/{args.total_batches}:"
    summary += f"\n- Successfully re-scraped: {success_count}"
    summary += f"\n- Failed to re-scrape: {failure_count}"
    
    print(summary)
    logging.info(summary)
    
    if failure_count > 0:
        log_message = f"Check {failure_log} and {detailed_log} for details on failed re-scraping attempts"
        print(log_message)
        logging.info(log_message)

if __name__ == "__main__":
    main()
