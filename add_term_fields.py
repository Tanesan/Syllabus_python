"""
all.json の各科目に 時限X_term フィールドを追加する。
docs/all/*.json の 項番No. の学期情報から生成。
既に 時限X_term がある場合はスキップする。
"""
import json
import os

with open('docs/all.json', 'r', encoding='utf-8') as f:
    all_data = json.load(f)

updated = 0
multi_semester = 0

for subject_id, subject in all_data.items():
    # 既に全ての時限に _term があればスキップ
    slot_idx = 1
    all_have_term = True
    while f'時限{slot_idx}' in subject:
        if f'時限{slot_idx}_term' not in subject:
            all_have_term = False
            break
        slot_idx += 1
    if all_have_term and slot_idx > 1:
        continue

    detail_path = f'docs/all/{subject_id}.json'
    if not os.path.isfile(detail_path):
        continue
    with open(detail_path, 'r', encoding='utf-8') as f:
        detail = json.load(f)

    eval_data = detail.get('評価', {})
    if not eval_data:
        continue

    semester_set = set()
    slot_idx = 1
    while f'時限{slot_idx}' in subject:
        koubann_key = f'項番No.{slot_idx}'
        if koubann_key in eval_data:
            entry = eval_data[koubann_key]
            if isinstance(entry, list) and len(entry) > 1:
                term_str = str(entry[1])
                if '春' in term_str or 'Spring' in term_str:
                    subject[f'時限{slot_idx}_term'] = 0
                    semester_set.add(0)
                elif '秋' in term_str or 'Fall' in term_str:
                    subject[f'時限{slot_idx}_term'] = 1
                    semester_set.add(1)
                else:
                    subject[f'時限{slot_idx}_term'] = -1
                    semester_set.add(-1)
                updated += 1
        slot_idx += 1

    if {0, 1}.issubset(semester_set) and subject.get('開講期') != 0:
        subject['開講期'] = 0
        multi_semester += 1

with open('docs/all.json', 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False)

print(f'Updated {updated} time slot terms, fixed {multi_semester} to year-round')
