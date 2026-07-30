"""「未分類」トップカテゴリの修正スクリプト

parse_graduation_requirements.py は、カテゴリヘッダより前に科目行が現れると
暫定カテゴリ「未分類」を作る。一部学部 (経済/理/工/教育/生命環境など) では
学則PDF上の「総合教育科目」見出しが抽出できず、キリスト教科目・言語教育科目
などの総合教育科目群がすべて「未分類」トップに入ってしまっていた。

その結果、アプリの単位集計で category_path のトップが要件カテゴリ
(総合教育科目) と一致せず、キリスト教学などが自由科目へ落ちる不具合が
発生していた (2026-07 ユーザー報告)。

このスクリプトは生成済みの docs/graduation_requirements_YYYY.json に対し:
  トップ名が「未分類」かつ サブカテゴリに「キリスト教科目」を含み、
  その学部の要件カテゴリに「総合教育科目」が存在する場合
  → トップ名を「総合教育科目」へリネーム (既存同名トップがあればマージ)
を適用する。適用後は build_subject_classifications.py を再実行して
subject_classifications_YYYY.json も更新すること。

使用方法:
  python3 fix_uncategorized_category.py          # 全年度
  python3 fix_uncategorized_category.py 2026     # 単一年度
"""
import json
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parent / "docs"

TARGET_NAME = "未分類"
RENAME_TO = "総合教育科目"
MARKER_SUBCATEGORY = "キリスト教科目"


def dept_requirement_categories(dept_data) -> set:
    names = set()
    reqs = dept_data.get("graduation_requirements", {})
    for r in reqs.get("requirements", []):
        if r.get("category"):
            names.add(r["category"])
    for sub in reqs.get("subdepartments", {}).values():
        for r in sub.get("requirements", []):
            if r.get("category"):
                names.add(r["category"])
    return names


def fix_department(dept_name: str, dept_data: dict) -> list:
    """学部内の未分類トップをリネーム。変更ログの文字列リストを返す。"""
    changes = []
    req_cats = dept_requirement_categories(dept_data)
    if RENAME_TO not in req_cats or TARGET_NAME in req_cats:
        return changes

    for sub_name, sub_data in dept_data.get("subdepartments", {}).items():
        cats = sub_data.get("categories", [])
        target = None
        existing = None
        for c in cats:
            if c.get("name") == TARGET_NAME:
                sub_names = [s.get("name", "") for s in c.get("subcategories", [])]
                if any(MARKER_SUBCATEGORY in s for s in sub_names):
                    target = c
            elif c.get("name") == RENAME_TO:
                existing = c
        if target is None:
            continue
        if existing is not None:
            # 既存の総合教育科目トップへマージ
            existing.setdefault("subcategories", []).extend(
                target.get("subcategories", [])
            )
            existing.setdefault("subjects", []).extend(target.get("subjects", []))
            cats.remove(target)
            changes.append(f"{dept_name}/{sub_name}: 未分類 を {RENAME_TO} へマージ")
        else:
            target["name"] = RENAME_TO
            changes.append(f"{dept_name}/{sub_name}: 未分類 → {RENAME_TO}")
    return changes


def fix_file(path: Path) -> bool:
    data = json.loads(path.read_text(encoding="utf-8"))
    all_changes = []
    for dept_name, dept_data in data.get("departments", {}).items():
        all_changes.extend(fix_department(dept_name, dept_data))
    if not all_changes:
        print(f"{path.name}: 変更なし")
        return False
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"{path.name}:")
    for c in all_changes:
        print(f"  - {c}")
    return True


def main():
    years = sys.argv[1:] or ["2022", "2023", "2024", "2025", "2026"]
    changed = False
    for y in years:
        p = DOCS / f"graduation_requirements_{y}.json"
        if not p.exists():
            print(f"{p.name}: なし (スキップ)")
            continue
        changed |= fix_file(p)
    if changed:
        print("\n次に build_subject_classifications.py を再実行してください:")
        print("  python3 build_subject_classifications.py all")


if __name__ == "__main__":
    main()
