"""
科目分類インデックス生成スクリプト

卒業要件JSON (docs/graduation_requirements_YYYY.json) と
全科目JSON (docs/all/*.json) から、
科目IDごとに「どの学部/学科/カテゴリに該当するか」を列挙した
インデックスJSONを生成する。

使用方法:
  # 単一年度
  python3 build_subject_classifications.py 2026

  # 全年度
  python3 build_subject_classifications.py all

出力: docs/subject_classifications_YYYY.json
"""
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
DOCS = BASE / "docs"
ALL_DIR = DOCS / "all"

SUBJECT_NAME_KEY = "【科目ナンバー/Course Number】授業名称"


def normalize_subject_name(name: str) -> str:
    """Flutter版と同じ正規化ルール"""
    if not name:
        return ""
    s = name.strip()
    # 科目番号を除去: 【200】哲学A → 哲学A
    s = re.sub(r"【\d{1,3}】", "", s)
    # 英名併記を除去: 哲学A／Philosophy A → 哲学A
    if "\uFF0F" in s:  # full-width slash ／
        s = s.split("\uFF0F", 1)[0]
    # 半角スラッシュ
    if "/" in s and not s.startswith("/"):
        s = s.split("/", 1)[0]
    # 全角空白除去
    s = s.replace("\u3000", "")
    return s.strip()


def build_subject_index():
    """全科目JSONから {正規化済み科目名: [id, ...]} の逆引きを構築"""
    index = defaultdict(list)
    if not ALL_DIR.is_dir():
        print(f"Warning: {ALL_DIR} not found, no subjects loaded.")
        return index

    count = 0
    for p in ALL_DIR.iterdir():
        if not p.is_file() or not p.name.endswith(".json"):
            continue
        try:
            with p.open(encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        subject_id = data.get("id") or p.stem
        raw_name = data.get(SUBJECT_NAME_KEY) or data.get("name") or ""
        normalized = normalize_subject_name(raw_name)
        if normalized:
            index[normalized].append(str(subject_id))
            count += 1
    print(f"Indexed {count} subjects into {len(index)} unique normalized names.")
    return index


def walk_categories(categories, path, collector):
    """カテゴリを再帰走査して collector.append((path_tuple, subject_name)) を呼ぶ"""
    for cat in categories or []:
        if not isinstance(cat, dict):
            continue
        cat_name = cat.get("name", "")
        current_path = path + [cat_name] if cat_name else path
        for subj in cat.get("subjects", []) or []:
            if isinstance(subj, dict):
                name = subj.get("name", "")
                if name:
                    collector.append((tuple(current_path), name))
        subcats = cat.get("subcategories")
        if subcats:
            walk_categories(subcats, current_path, collector)


def build_classifications(entry_year: int, subject_index):
    req_path = DOCS / f"graduation_requirements_{entry_year}.json"
    if not req_path.exists():
        print(f"Skip {entry_year}: {req_path} not found.")
        return None

    with req_path.open(encoding="utf-8") as f:
        req_data = json.load(f)

    classifications = defaultdict(list)
    departments = req_data.get("departments", {})

    for dept_name, dept_data in departments.items():
        if not isinstance(dept_data, dict):
            continue
        subdepts = dept_data.get("subdepartments", {}) or {}
        for sub_name, sub_data in subdepts.items():
            if not isinstance(sub_data, dict):
                continue
            collector = []
            walk_categories(sub_data.get("categories", []), [], collector)
            for category_path, subject_name in collector:
                normalized = normalize_subject_name(subject_name)
                if not normalized:
                    continue
                ids = subject_index.get(normalized, [])
                for sid in ids:
                    entry = {
                        "department": dept_name,
                        "subdepartment": sub_name if sub_name != "_default" else None,
                        "category_path": list(category_path),
                        "subject_name_in_requirement": subject_name,
                    }
                    # サブ学科が _default の場合は None で統一、同一エントリの重複排除
                    existing = classifications[sid]
                    key = (
                        entry["department"],
                        entry["subdepartment"],
                        tuple(entry["category_path"]),
                        entry["subject_name_in_requirement"],
                    )
                    if key not in {
                        (
                            e["department"],
                            e["subdepartment"],
                            tuple(e["category_path"]),
                            e["subject_name_in_requirement"],
                        )
                        for e in existing
                    }:
                        existing.append(entry)

    result = {
        "entry_year": entry_year,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": req_path.name,
        "classifications": dict(classifications),
    }
    out_path = DOCS / f"subject_classifications_{entry_year}.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, separators=(",", ":"))
    matched = len(classifications)
    total_entries = sum(len(v) for v in classifications.values())
    print(
        f"{entry_year}: {matched} subjects matched, {total_entries} classification entries. "
        f"→ {out_path.name}"
    )
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 build_subject_classifications.py <year|all>")
        sys.exit(1)

    target = sys.argv[1]
    subject_index = build_subject_index()

    if target.lower() == "all":
        years = []
        for p in DOCS.glob("graduation_requirements_*.json"):
            m = re.search(r"graduation_requirements_(\d{4})\.json", p.name)
            if m:
                years.append(int(m.group(1)))
        for y in sorted(years):
            build_classifications(y, subject_index)
    else:
        try:
            y = int(target)
        except ValueError:
            print(f"Invalid year: {target}")
            sys.exit(1)
        build_classifications(y, subject_index)


if __name__ == "__main__":
    main()
