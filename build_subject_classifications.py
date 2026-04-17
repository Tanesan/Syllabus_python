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

# 学部名 → 管理部署 index の対応 (define.py の ad_data と一致)
DEPARTMENT_AD_INDEX = {
    "神学部": 0,
    "文学部": 1,
    "社会学部": 2,
    "法学部": 3,
    "経済学部": 4,
    "商学部": 5,
    # 旧 理工学部 (6) は 2021 以前のみ
    "総合政策学部": 7,
    "人間福祉学部": 8,
    "教育学部": 9,
    "国際学部": 10,
    "理学部": 11,
    "工学部": 12,
    "生命環境学部": 13,
    "建築学部": 14,
    # 全学科目 は複数の部署にまたがるため None
}

# 学部 → 関連する管理部署の広い集合 (開講学部が関連センターのケースも含む)
# 例: 教育学部の要件に「教職教育研究センター」の科目が含まれることがある
DEPARTMENT_EXTENDED_INDICES = {
    "神学部": {0},
    "文学部": {1, 23, 24, 26},  # キリスト教と文化研究センター等
    "社会学部": {2},
    "法学部": {3},
    "経済学部": {4},
    "商学部": {5},
    "総合政策学部": {7},
    "人間福祉学部": {8},
    "教育学部": {9, 23, 24},  # 教職教育研究センター（資格/教職専門）
    "国際学部": {10, 25, 27},  # 国際教育・協力センター、日本語教育
    "理学部": {11},
    "工学部": {12},
    "生命環境学部": {13},
    "建築学部": {14},
}


_ROMAN_MAP = [
    ("Ⅰ", "I"), ("Ⅱ", "II"), ("Ⅲ", "III"), ("Ⅳ", "IV"), ("Ⅴ", "V"),
    ("Ⅵ", "VI"), ("Ⅶ", "VII"), ("Ⅷ", "VIII"), ("Ⅸ", "IX"), ("Ⅹ", "X"),
    ("ⅰ", "i"), ("ⅱ", "ii"), ("ⅲ", "iii"), ("ⅳ", "iv"), ("ⅴ", "v"),
]


def normalize_subject_name(name: str) -> str:
    """卒業要件JSON と 科目JSON の科目名を統一正規化する。

    処理順:
      1. 科目番号接頭 【000】 を除去
      2. 全角空白での分割（all/*.json はセクション番号が 全角空白の後ろに付く）
      3. 英名併記 ／ または / で分割
      4. 全ての空白を削除
      5. 全角ローマ数字を ASCII に変換（Ⅰ → I）
      6. 全角数字を半角に
      7. 全角英字を半角に
    """
    if not name:
        return ""
    s = name.strip()
    # 1. 科目番号
    s = re.sub(r"【\d{1,3}】", "", s)
    # 2. 全角空白分割（セクション番号除去）
    if "\u3000" in s:
        s = s.split("\u3000", 1)[0]
    # 3. 英名併記除去
    if "\uFF0F" in s:
        s = s.split("\uFF0F", 1)[0]
    if "/" in s and not s.startswith("/"):
        s = s.split("/", 1)[0]
    # 4. 空白全削除
    s = re.sub(r"\s+", "", s)
    # 5. ローマ数字
    for old, new in _ROMAN_MAP:
        s = s.replace(old, new)
    # 6/7. 全角英数字→半角
    s = s.translate(
        str.maketrans(
            "ＡBＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ０１２３４５６７８９",
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
        )
    )
    return s.strip()


def _extract_english_name(raw: str) -> str:
    """all.json 形式 '【100】日本語名　1／English Name' から英名部分を取り出す"""
    if not raw or "\uFF0F" not in raw:
        return ""
    after = raw.split("\uFF0F", 1)[1]
    # 英名側にも末尾に空白+数字（セクション番号）がつく場合があるので削除
    after = re.sub(r"\s+\d+\s*$", "", after)
    after = after.strip()
    return after


def build_subject_index():
    """全科目JSONから逆引きインデックスを構築。
    戻り値:
      name_to_ids: {正規化済み科目名: [id, ...]}
      id_to_ad:    {id: 管理部署インデックス}
    """
    name_to_ids = defaultdict(list)
    id_to_ad = {}
    if not ALL_DIR.is_dir():
        print(f"Warning: {ALL_DIR} not found, no subjects loaded.")
        return name_to_ids, id_to_ad

    count = 0
    for p in ALL_DIR.iterdir():
        if not p.is_file() or not p.name.endswith(".json"):
            continue
        try:
            with p.open(encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        subject_id = str(data.get("id") or p.stem)
        raw_name = data.get(SUBJECT_NAME_KEY) or data.get("name") or ""

        ad_index = data.get("管理部署")
        if isinstance(ad_index, int):
            id_to_ad[subject_id] = ad_index

        # 日本語名（／の前） を登録
        normalized = normalize_subject_name(raw_name)
        if normalized:
            name_to_ids[normalized].append(subject_id)

        # 英語名（／の後） も登録
        english = _extract_english_name(raw_name)
        if english:
            en_normalized = normalize_subject_name(english)
            if en_normalized and en_normalized != normalized:
                name_to_ids[en_normalized].append(subject_id)

        count += 1
    # 重複ID除去
    for k in list(name_to_ids.keys()):
        name_to_ids[k] = sorted(set(name_to_ids[k]))
    print(
        f"Indexed {count} subjects into {len(name_to_ids)} unique normalized names."
    )
    return name_to_ids, id_to_ad


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


def _filter_ids_by_department(ids, id_to_ad, dept_name):
    """卒業要件側の学部名で管理部署フィルタを適用。
    フィルタ後が空になる場合はフィルタ前のリストをそのまま返す（保守的）。
    """
    allowed = DEPARTMENT_EXTENDED_INDICES.get(dept_name)
    if allowed is None:
        # 全学科目などは絞らない
        return ids
    filtered = [i for i in ids if id_to_ad.get(i) in allowed]
    return filtered if filtered else ids


def build_classifications(entry_year: int, subject_index_tuple):
    req_path = DOCS / f"graduation_requirements_{entry_year}.json"
    if not req_path.exists():
        print(f"Skip {entry_year}: {req_path} not found.")
        return None

    name_to_ids, id_to_ad = subject_index_tuple

    with req_path.open(encoding="utf-8") as f:
        req_data = json.load(f)

    classifications = defaultdict(list)
    filter_stats = {"applied": 0, "fallback": 0, "no_match": 0}
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
                raw_ids = name_to_ids.get(normalized, [])
                if not raw_ids:
                    filter_stats["no_match"] += 1
                    continue
                # 管理部署で絞り込み（全学科目は None を返す → 絞らない）
                ids = _filter_ids_by_department(raw_ids, id_to_ad, dept_name)
                if ids is raw_ids and DEPARTMENT_EXTENDED_INDICES.get(dept_name) is not None and raw_ids:
                    # フィルタ適用後に全件ゼロ → フォールバックした
                    # （_filter_ids_by_department は fallback時に元のlistを返す）
                    if not any(id_to_ad.get(i) in DEPARTMENT_EXTENDED_INDICES[dept_name] for i in raw_ids):
                        filter_stats["fallback"] += 1
                    else:
                        filter_stats["applied"] += 1
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
        f"{entry_year}: {matched} subjects matched, {total_entries} entries "
        f"(dept-filtered={filter_stats['applied']}, fallback={filter_stats['fallback']}, "
        f"no-match={filter_stats['no_match']})"
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
