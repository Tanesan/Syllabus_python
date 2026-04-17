"""
学則PDFから卒業要件・科目カテゴリ情報を抽出するスクリプト。

使用方法:
  python3 parse_graduation_requirements.py input.pdf output.json

出力JSONの構造:
{
  "entry_year": 2026,
  "source_pdf": "kwu_rules_20260401.pdf",
  "generated_at": "2026-04-17T12:00:00",
  "departments": {
    "社会学部": {
      "subdepartments": {
        "社会学科": {
          "categories": [
            {
              "name": "Ⅰ群科目（必修科目）",
              "subjects": [
                {"name": "社会学A", "credits": 2},
                ...
              ]
            }
          ],
          "graduation_requirements": [
            {"category": "Ⅰ群科目（必修科目）", "required_credits": 40},
            ...
          ],
          "total_required_credits": 124
        }
      }
    }
  }
}

このスクリプトは粗い抽出を行うため、出力後に手動チェック・補正が推奨される。
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import pdfplumber

# 全角数字→半角
ZEN2HAN = str.maketrans("０１２３４５６７八九", "0123456789")
FULL_TO_HALF = str.maketrans(
    "０１２３４５６７８９", "0123456789"
)

# ノイズ行（学則ヘッダ・フッタ等）
NOISE_PATTERNS = [
    re.compile(r"^【関西学院大学"),
    re.compile(r"^\d+/\d+$"),  # ページ番号
]

# 科目行のパターン: 「科目名 数字」が繰り返されるフォーマット
# 例: "キリスト教学A ２ キリスト教学B ２ キリスト教学演習A ２"
# 「1科目各X～Y単位」のような変動単位も扱う
SUBJECT_TOKEN = re.compile(
    r"([^\s０-９]+?)\s*"
    r"(?:([０-９0-9]+)|\(([^)]*?\d[^)]*?)単位\))"
)

# 第N節 ○○部 の区切り
SECTION_RE = re.compile(r"^第(\d+)節\s+(.+?)$")

# 第N条 の区切り（節内でサブセクション）
ARTICLE_RE = re.compile(r"^第(\d+)条(?:の\d+)?\s+(.+?)$")

# 章の区切り
CHAPTER_RE = re.compile(r"^第(\d+)章\s+(.+?)$")

# 項番号 (１, ２, 3項目など)
NUMBERED_ITEM = re.compile(r"^([０-９0-9]+)\s+(.+)$")

# カテゴリらしい行（科目を含まない、短いラベル）
# 「XX科目」「XX科目群」「XX演習」「卒業論文」等
CATEGORY_HINTS = [
    "科目", "科目群", "演習", "卒業論文", "卒業研究", "卒業演習",
    "入門", "講義", "実習", "関連", "必修", "選択", "自由",
]


def clean_text(text: str) -> str:
    """全角数字を半角に、余分な空白を正規化"""
    return text.translate(FULL_TO_HALF).strip()


def is_noise_line(line: str) -> bool:
    for p in NOISE_PATTERNS:
        if p.search(line):
            return True
    return False


def is_category_header(line: str) -> bool:
    """カテゴリヘッダ行の判定（単位数の出現パターンなし、短い）"""
    if len(line) > 40:
        return False
    # 数字を含むならカテゴリでない可能性が高い（ただし例外あり）
    if re.search(r"[0-9０-９]", line):
        return False
    # カテゴリらしい単語を含む
    for hint in CATEGORY_HINTS:
        if hint in line:
            return True
    return False


def is_likely_extraction_error(name: str) -> bool:
    """科目名が1文字以下、または抽出ミスと判定される場合 True"""
    if not name:
        return True
    # 1文字の科目名（Ⅰ, Ⅱ, A, B 等）は誤抽出
    if len(name) <= 1:
        return True
    # 2文字で末尾が数字1桁の場合も怪しい（例: "A1"）
    return False


def parse_subjects_from_line(line: str):
    """一行から「科目名 単位数」のペアを全て抽出。

    対応フォーマット:
      - 「科目名 N」 (Nは全角/半角数字)
      - 「科目名（1科目各N～M単位）」 (変動単位)
      - 「科目名（1科目N～M単位）」 (変動単位の別形式)
      - 「科目名（1科目N又はM単位）」 (2値単位)
    """
    subjects = []
    # 全角→半角・カッコ正規化
    converted = line.translate(FULL_TO_HALF)
    converted = converted.replace("（", "(").replace("）", ")")

    # 変動単位系: 「(1科目各N~M単位)」「(1科目N~M単位)」「(1科目各N単位)」
    # ～ は全角(U+FF5E) or 半角(~) or 〜(U+301C)
    var_patterns = [
        re.compile(r"(1科目各?\s*\d+[～~〜]\d+単位)"),
        re.compile(r"(1科目各?\s*\d+\s*又は\s*\d+\s*単位)"),
        re.compile(r"(1科目各?\s*\d+単位)"),
    ]
    # 科目名 + "(変動単位)"
    full_var = re.compile(
        r"(\S+?)\s*\(("
        r"1科目各?\s*\d+[～~〜]\d+単位|"
        r"1科目各?\s*\d+\s*又は\s*\d+\s*単位|"
        r"1科目各?\s*\d+単位"
        r")\)"
    )
    for m in full_var.finditer(converted):
        name = m.group(1).strip()
        detail = m.group(2)
        if is_likely_extraction_error(name):
            continue
        # 数値取り出し
        nums = [int(n) for n in re.findall(r"\d+", detail)]
        entry = {"name": name, "variable": True, "detail": f"({detail})"}
        if "~" in detail or "～" in detail or "〜" in detail:
            entry["credits_min"] = nums[-2] if len(nums) >= 2 else nums[0]
            entry["credits_max"] = nums[-1]
        elif "又は" in detail:
            entry["credits_options"] = nums[-2:]
        else:
            entry["credits"] = nums[-1]
        subjects.append(entry)
    # 変動単位部分を削除
    cleaned = full_var.sub(" ", converted)

    # 「科目名 数字」パターン（最も一般的）
    # 数字は1-2桁
    # ただし、英語科目のように「English Communication A 1」は
    # 「English Communication A」が科目名で「1」が単位数
    # 逆向きに走査し、数字トークンの前の連続非数字トークンを結合する
    tokens = re.split(r"\s+", cleaned.strip())
    tokens = [t for t in tokens if t]
    i = 0
    current_name_parts = []
    while i < len(tokens):
        tok = tokens[i]
        # 数字?
        if re.fullmatch(r"\d{1,2}", tok):
            if current_name_parts:
                name = " ".join(current_name_parts).strip()
                if not is_likely_extraction_error(name):
                    subjects.append({"name": name, "credits": int(tok)})
                current_name_parts = []
            i += 1
            continue
        # 非数字 → 科目名の一部として蓄積
        current_name_parts.append(tok)
        i += 1
    return subjects


def extract_sections(pdf_path):
    """PDFから節ごとにテキストを分割"""
    full_text_lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for line in text.split("\n"):
                line = line.strip()
                if not line or is_noise_line(line):
                    continue
                full_text_lines.append(line)
    return full_text_lines


def parse_graduation_requirements_page(lines, start_idx):
    """第17節 卒業必要単位数 から各学部の要件をパース。
    カテゴリ名が改行で分断されるケース (例: 「Ⅳ群科目（自由\n選択科目）」) に対応。
    """
    requirements = {}
    # 第17節〜第18節の範囲のみ抜粋
    end_idx = start_idx
    for j in range(start_idx, len(lines)):
        if re.match(r"^第18節", lines[j]):
            end_idx = j
            break
    if end_idx == start_idx:
        end_idx = len(lines)
    section_lines = lines[start_idx:end_idx]

    # 「○○単位」で終わる行が要件行。
    # その前行が要件行でない場合は、前行と結合する。
    # さらにその前の前行が「X単位」で終わってなければ結合、繰り返す。
    merged = []
    buffer = ""
    for line in section_lines:
        conv = line.translate(FULL_TO_HALF)
        if re.search(r"\d+単位$", conv):
            if buffer:
                merged.append((buffer + line).strip())
                buffer = ""
            else:
                merged.append(line)
        else:
            # カテゴリ区切り判定（学部行・学科行は単独行）
            if (
                re.match(r"^\d+\s+.+?学部$", line.translate(FULL_TO_HALF))
                or re.match(r".+(?:学科|コース|課程)$", line)
                and len(line) < 30
            ):
                if buffer:
                    merged.append(buffer.strip())
                    buffer = ""
                merged.append(line)
            else:
                # カテゴリ名の続きと推定
                if buffer:
                    buffer += line
                else:
                    buffer = line
    if buffer:
        merged.append(buffer.strip())

    current_department = None
    current_subdept = None
    for line in merged:
        if re.match(r"^第18節", line):
            break
        # 「1 神学部」「2 文学部」など（学部区切り）
        m = re.match(r"^\d+\s+(.+?学部)$", clean_text(line))
        if m:
            current_department = m.group(1)
            requirements.setdefault(current_department, {"subdepartments": {}})
            current_subdept = None
            continue
        # 「社会学科」「文化歴史学科」など
        if re.match(r".+(?:学科|コース|課程)$", line) and len(line) < 30:
            current_subdept = line
            if current_department:
                requirements[current_department]["subdepartments"].setdefault(
                    current_subdept, {"requirements": [], "total_required_credits": 0}
                )
            continue
        # 「キリスト教科目 8単位」「計 128単位」系
        converted = line.translate(FULL_TO_HALF)
        m2 = re.match(r"^(.+?)\s+(\d+)単位$", converted)
        if not m2:
            m2 = re.match(r"^(.+?)(\d+)単位$", converted)  # 空白なしも対応
        if m2:
            cat_name = m2.group(1).strip()
            # 接頭の番号（「1 キリスト教科目」→「キリスト教科目」）を除去
            cat_name = re.sub(r"^\d+\s+", "", cat_name)
            credits = int(m2.group(2))
            # 「計 124単位」「合計128単位」「上記を含めて合計128単位」等
            if re.search(r"(計|合計)$", cat_name) or "合計" in cat_name:
                if current_department and current_subdept:
                    requirements[current_department]["subdepartments"][current_subdept][
                        "total_required_credits"
                    ] = credits
                elif current_department:
                    requirements[current_department]["total_required_credits"] = credits
            elif "卒業必要単位数" in cat_name:
                if current_department and current_subdept:
                    requirements[current_department]["subdepartments"][current_subdept][
                        "total_required_credits"
                    ] = credits
                elif current_department:
                    requirements[current_department]["total_required_credits"] = credits
            else:
                if current_department and current_subdept:
                    requirements[current_department]["subdepartments"][current_subdept][
                        "requirements"
                    ].append({"category": cat_name, "required_credits": credits})
                elif current_department:
                    requirements[current_department].setdefault(
                        "requirements", []
                    ).append({"category": cat_name, "required_credits": credits})
    return requirements


# トップレベル的なカテゴリ名（これが出現したら親-子関係をリセット）
TOP_LEVEL_KEYWORDS = [
    "キリスト教", "言語教育", "教養", "演習", "卒業論文", "卒業研究",
    "卒業演習", "基礎科目群", "専門科目群", "教職", "共通科目",
    "基礎科目", "専門科目", "総合科目", "入門科目", "自由",
    "共通教育", "専門教育", "基礎教育", "専門基礎", "専門応用",
    "領域関連", "地域研究",
]


def is_top_level_category(name: str) -> bool:
    for kw in TOP_LEVEL_KEYWORDS:
        if name.startswith(kw) or (kw in name and "群" in name):
            return True
    return False


def nest_categories(categories):
    """空カテゴリを親カテゴリとして、後続を子として階層化する。"""
    result = []
    i = 0
    while i < len(categories):
        cat = categories[i]
        if not cat.get("subjects"):
            # 親候補 → 後続カテゴリを子として収集
            parent = {"name": cat["name"], "subcategories": []}
            j = i + 1
            while j < len(categories):
                nxt = categories[j]
                # 次のトップレベルに到達したら終了
                if is_top_level_category(nxt["name"]):
                    break
                # 次も空カテゴリなら、これも親候補 → 孫階層（再帰的に処理）
                parent["subcategories"].append(nxt)
                j += 1
            # subcategories が空ならトップレベル扱いで元に戻す
            if parent["subcategories"]:
                result.append(parent)
                i = j
            else:
                result.append(cat)
                i += 1
        else:
            result.append(cat)
            i += 1
    return result


# 学部注釈: 学則には学部全体の要件のみで、学科別詳細は履修要綱参照
DEPARTMENT_NOTES = {
    "総合政策学部": "学則には学部全体の卒業要件のみ記載されています。各学科（総合政策学科・メディア情報学科・都市政策学科・国際政策学科）ごとの必修科目・選択必修の詳細は、履修要綱（ハンドブック）を各自ご確認ください。",
    "商学部": "学則には学部全体の卒業要件のみ記載されています。各コース（マーケティングコース・ファイナンスコース等）ごとの必修科目の詳細は、履修要綱を各自ご確認ください。",
    "法学部": "学則には学部全体の卒業要件のみ記載されています。各学科（法律学科・政治学科）・各コースごとの必修科目の詳細は、履修要綱を各自ご確認ください。",
    "経済学部": "学則には学部全体の卒業要件のみ記載されています。コース・フィールドごとの必修科目の詳細は、履修要綱を各自ご確認ください。",
    "国際学部": "学則には学部全体の卒業要件のみ記載されています。各領域の必修科目の詳細は、履修要綱を各自ご確認ください。",
    "人間福祉学部": "学則には学部全体の卒業要件のみ記載されています。各学科（社会福祉学科・社会起業学科・人間科学科）の必修科目の詳細は、履修要綱を各自ご確認ください。",
    "理学部": "学則には学部全体の卒業要件のみ記載されています。各学科（数理科学科・物理・宇宙学科・化学科）の必修科目の詳細は、履修要綱を各自ご確認ください。",
    "工学部": "学則には学部全体の卒業要件のみ記載されています。各課程（物質工学・電気電子応用工学・情報工学・知能・機械工学）の必修科目の詳細は、履修要綱を各自ご確認ください。",
    "生命環境学部": "学則には学部全体の卒業要件のみ記載されています。各学科（生物科学・生命医科学・環境応用化学）の必修科目の詳細は、履修要綱を各自ご確認ください。",
    "教育学部": "学則には学部全体の卒業要件のみ記載されています。各コース（幼児教育学・初等教育学・教育科学）の必修科目の詳細は、履修要綱を各自ご確認ください。",
}


def parse(pdf_path):
    lines = extract_sections(pdf_path)
    # 節の境界を検索
    section_indices = []
    for i, line in enumerate(lines):
        m = SECTION_RE.match(line)
        if m:
            section_indices.append((i, m.group(1), m.group(2)))

    result = {
        "entry_year": None,
        "source_pdf": Path(pdf_path).name,
        "generated_at": datetime.now().isoformat(),
        "departments": {},
    }

    # 入学年度 (ファイル名やテキストから推測)
    match = re.search(r"(\d{4})年度入学生用", "\n".join(lines[:20]))
    if match:
        result["entry_year"] = int(match.group(1))

    # 第17節（卒業要件）の位置を探して先にパース
    graduation_reqs = {}
    for idx, num, name in section_indices:
        if name == "卒業必要単位数":
            graduation_reqs = parse_graduation_requirements_page(lines, idx)
            break

    # 各学部セクション (第2節〜第16節) をパース
    for sec_i, (idx, num, name) in enumerate(section_indices):
        if not name.endswith("部") and name != "全学科目":
            continue
        # 区切り範囲
        next_idx = (
            section_indices[sec_i + 1][0]
            if sec_i + 1 < len(section_indices)
            else len(lines)
        )
        dept_lines = lines[idx + 1 : next_idx]

        dept_data = {
            "section_number": int(num),
            "subdepartments": {},
        }

        # サブセクション（学科/コース/課程）とカテゴリを順次抽出
        current_subdept = "_default"
        current_category = None
        dept_data["subdepartments"][current_subdept] = {"categories": []}

        for line in dept_lines:
            # 第N条 の記述はメタ情報としてスキップ
            if ARTICLE_RE.match(line):
                continue
            # 学科/コース/課程の区切り
            m_sub = re.match(r"^(.{2,20}(?:学科|コース|課程))$", line)
            if m_sub and not is_category_header(line):
                current_subdept = m_sub.group(1)
                dept_data["subdepartments"].setdefault(
                    current_subdept, {"categories": []}
                )
                current_category = None
                continue
            # カテゴリヘッダ
            if is_category_header(line):
                current_category = {"name": line, "subjects": []}
                dept_data["subdepartments"][current_subdept]["categories"].append(
                    current_category
                )
                continue
            # 科目行
            if current_category is None:
                # 暫定カテゴリを作成
                current_category = {"name": "未分類", "subjects": []}
                dept_data["subdepartments"][current_subdept]["categories"].append(
                    current_category
                )
            subjects = parse_subjects_from_line(line)
            current_category["subjects"].extend(subjects)

        # 空のサブセクションを整理 + 階層化
        for sub_name, sub_data in dept_data["subdepartments"].items():
            sub_data["categories"] = nest_categories(sub_data["categories"])
        dept_data["subdepartments"] = {
            k: v for k, v in dept_data["subdepartments"].items()
            if v.get("categories")
        }

        # 卒業要件を紐付け
        if name in graduation_reqs:
            dept_data["graduation_requirements"] = graduation_reqs[name]

        # 注釈を追加
        if name in DEPARTMENT_NOTES:
            dept_data["note"] = DEPARTMENT_NOTES[name]

        result["departments"][name] = dept_data

    return result


def main():
    if len(sys.argv) < 3:
        print("Usage: parse_graduation_requirements.py input.pdf output.json")
        sys.exit(1)
    pdf_path = sys.argv[1]
    output_path = sys.argv[2]
    data = parse(pdf_path)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Wrote {output_path}")
    # サマリー表示
    print(f"Entry year: {data['entry_year']}")
    print(f"Departments: {len(data['departments'])}")
    for name, dept in data["departments"].items():
        sub_count = len(dept.get("subdepartments", {}))
        print(f"  {name}: {sub_count} subdepartments")


if __name__ == "__main__":
    main()
