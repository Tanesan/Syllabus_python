"""
all.json の各科目に 時限X_term フィールドを追加/修正する。
docs/all/*.json の 履修期・項番No. から正確な開講期と_termを決定。
"""
import json
import os

# 履修期テキスト → 開講期番号
RISHUKI_MAP = {
    "通年": 0,
    "春学期": 1, "秋学期": 2,
    "春学期前半": 3, "春学期後半": 4,
    "秋学期前半": 5, "秋学期後半": 6,
    "通年集中": 7,
    "春学期集中": 8, "秋学期集中": 9,
    "春学期前半集中": 10, "春学期後半集中": 11,
    "秋学期前半集中": 12, "秋学期後半集中": 13,
}

# 開講期 → _term マッピング
KAIKO_TO_TERM = {
    0: -1, 1: 0, 2: 1, 3: 0, 4: 0, 5: 1, 6: 1,
    7: -1, 8: 0, 9: 1, 10: 0, 11: 0, 12: 1, 13: 1,
}

with open('docs/all.json', 'r', encoding='utf-8') as f:
    all_data = json.load(f)

updated_terms = 0
fixed_kaiko = 0

for subject_id, subject in all_data.items():
    detail_path = f'docs/all/{subject_id}.json'
    if not os.path.isfile(detail_path):
        continue
    with open(detail_path, 'r', encoding='utf-8') as f:
        detail = json.load(f)

    # 1. 履修期から開講期を修正
    rishuki = detail.get('履修期', '')
    for key_text, kaiko_val in RISHUKI_MAP.items():
        if rishuki == key_text:
            if subject.get('開講期') != kaiko_val:
                subject['開講期'] = kaiko_val
                fixed_kaiko += 1
            break

    kaiko = subject.get('開講期')
    if kaiko is None:
        continue

    base_term = KAIKO_TO_TERM.get(kaiko, -1)
    is_year_round = kaiko in (0, 7)

    # 2. 時限X_term を設定
    eval_data = detail.get('評価', {})
    slot_idx = 1
    while f'時限{slot_idx}' in subject:
        old_val = subject.get(f'時限{slot_idx}_term')

        if is_year_round:
            # 通年: 項番No. の学期ラベルで春/秋を個別判定
            new_term = -1
            entry = eval_data.get(f'項番No.{slot_idx}')
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
            updated_terms += 1
        slot_idx += 1

with open('docs/all.json', 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False)

print(f'Fixed {fixed_kaiko} 開講期 values, updated {updated_terms} _term fields')
