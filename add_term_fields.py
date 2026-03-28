"""
all.json の各科目に 時限X_term フィールドを追加/修正する。
開講期から _term を決定する。通年科目のみ項番No.の学期ラベルで春/秋を区別。
"""
import json
import os

# 開講期 → _term マッピング
# 0=通年, 1=春, 2=秋, 3=春前半, 4=春後半, 5=秋前半, 6=秋後半
# 7=通年集中, 8=春集中, 9=秋集中, 10=春前半集中, 11=春後半集中, 12=秋前半集中, 13=秋後半集中
KAIKO_TO_TERM = {
    0: -1,  # 通年 (個別判定)
    1: 0,   # 春学期
    2: 1,   # 秋学期
    3: 0,   # 春学期前半
    4: 0,   # 春学期後半
    5: 1,   # 秋学期前半
    6: 1,   # 秋学期後半
    7: -1,  # 通年集中 (個別判定)
    8: 0,   # 春学期集中
    9: 1,   # 秋学期集中
    10: 0,  # 春学期前半集中
    11: 0,  # 春学期後半集中
    12: 1,  # 秋学期前半集中
    13: 1,  # 秋学期後半集中
}

with open('docs/all.json', 'r', encoding='utf-8') as f:
    all_data = json.load(f)

updated = 0

for subject_id, subject in all_data.items():
    kaiko = subject.get('開講期')
    if kaiko is None:
        continue

    base_term = KAIKO_TO_TERM.get(kaiko, -1)
    is_year_round = kaiko in (0, 7)

    slot_idx = 1
    while f'時限{slot_idx}' in subject:
        old_val = subject.get(f'時限{slot_idx}_term')

        if is_year_round:
            # 通年: 項番No. の学期ラベルで春/秋を個別判定
            detail_path = f'docs/all/{subject_id}.json'
            new_term = -1  # デフォルト: 通年
            if os.path.isfile(detail_path):
                with open(detail_path, 'r', encoding='utf-8') as f:
                    detail = json.load(f)
                entry = detail.get('評価', {}).get(f'項番No.{slot_idx}')
                if isinstance(entry, list) and len(entry) > 1:
                    term_str = str(entry[1])
                    if '春' in term_str or 'Spring' in term_str:
                        new_term = 0
                    elif '秋' in term_str or 'Fall' in term_str:
                        new_term = 1
            subject[f'時限{slot_idx}_term'] = new_term
        else:
            # 非通年: 開講期から一律決定
            subject[f'時限{slot_idx}_term'] = base_term

        if old_val != subject[f'時限{slot_idx}_term']:
            updated += 1
        slot_idx += 1

with open('docs/all.json', 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False)

print(f'Updated {updated} time slot terms')
