# 卒業要件機能 引き継ぎ書（next-syllabus / syllabus 向け）

## 概要

関西学院大学の学則PDFから卒業要件を抽出し、ユーザーが自分の時間割と照合して
「あと何単位必要か」を可視化する機能です。Flutter アプリ（time_schedule）で既に
実装済み。これを next-syllabus（Next.js）と kgu-syllabus.com（React）にも
移植したい。

## 配信中のデータ

### JSON配信エンドポイント
- `https://api.syllabus.tanemura.dev/graduation_requirements_2022.json`
- `https://api.syllabus.tanemura.dev/graduation_requirements_2023.json`
- `https://api.syllabus.tanemura.dev/graduation_requirements_2024.json`
- `https://api.syllabus.tanemura.dev/graduation_requirements_2025.json`
- `https://api.syllabus.tanemura.dev/graduation_requirements_2026.json`

各 JSON は入学年度別の卒業要件データ（学則PDFから自動抽出）。

### データ構造

```typescript
interface GraduationRequirements {
  entry_year: number | null;       // 例: 2026
  source_pdf: string;               // 元PDFファイル名
  generated_at: string;             // ISO8601
  departments: {
    [deptName: string]: Department; // 学部名 → 学部データ
  };
}

interface Department {
  section_number: number;           // 学則の第N節
  note?: string;                    // 学科別詳細なしの学部への案内
  subdepartments: {
    [subName: string]: {            // 学科/コース/課程
      categories: Category[];        // カテゴリ一覧
    };
  };
  graduation_requirements?: {        // 卒業要件
    subdepartments: object;          // 通常空（学部全体要件の場合）
    requirements: Requirement[];
    total_required_credits: number;  // 卒業必要総単位数 (例: 124)
  };
}

interface Category {
  name: string;                     // "キリスト教科目", "言語教育科目" 等
  subjects: Subject[];              // カテゴリ配下の科目
  subcategories?: Category[];       // 階層構造（空のsubjectsを持つ親カテゴリ）
}

interface Subject {
  name: string;                     // 科目名（例: "キリスト教学A"）
  credits?: number;                 // 単位数
  variable?: boolean;               // 変動単位フラグ
  credits_min?: number;             // 変動単位の最小
  credits_max?: number;             // 変動単位の最大
  credits_options?: number[];       // 2値単位の選択肢
  detail?: string;                  // 変動単位の原文 例: "(1科目各1~8単位)"
}

interface Requirement {
  category: string;                 // カテゴリ名 (Categoryのnameと一致する)
  required_credits: number;         // 必要単位数
}
```

## 実装の要点

### 1. 学科別詳細の制約

学則PDFには学部全体の卒業要件しか記載されていない学部があります（総合政策学部、商学部、
法学部、経済学部、国際学部、人間福祉学部、理学部、工学部、生命環境学部、教育学部）。
これらには `note` フィールドが設定されているので、UI上で必ず表示して
「学科別詳細は履修要綱参照」と案内してください。

### 2. 科目マッチング（重要）

ユーザーの時間割に登録されている科目と、JSONのカテゴリ配下の科目をマッチング
することで、カテゴリ別の取得単位数を算出します。

**マッチング上の注意:**
- 科目名の正規化が必要:
  - `【200】哲学A` → `哲学A`（科目番号除去）
  - `哲学A／Philosophy A` → `哲学A`（英名併記除去）
  - 全角空白 `　` → 削除
- 同じ科目名が複数カテゴリに存在する場合は最初にマッチしたカテゴリに計上
- 階層構造の場合は再帰的に全カテゴリを走査

### 3. カテゴリ名の不一致

```json
"graduation_requirements": {
  "requirements": [
    { "category": "キリスト教科目", "required_credits": 8 }
  ]
},
"subdepartments": {
  "社会学科": {
    "categories": [
      { "name": "キリスト教科目", "subjects": [...] }
    ]
  }
}
```
通常は一致していますが、学則側の表記揺れ（「専門科目群」vs「専門科目」等）が
あり得るので、完全一致しない場合はフロントエンドで部分一致ロジックを推奨。

### 4. 全学期の時間割を合算

ユーザーの時間割は 春/秋 × 年度 で別々のドキュメントに保存されています。
単位集計には **全学期の登録科目を合算** する必要があります。

Firestore パス例:
```
users/{uid}/timeSchedule_test2{termIndex}{yearValue}
```
例: `timeSchedule_test202026` = 2026年春学期

## UI ガイドライン（Flutter 実装参考）

### 画面構成
1. **入学年度セレクタ**（default 2026）
2. **学部セレクタ**（ドロップダウン、`departments` のキー）
3. **学科セレクタ**（選択した学部に `subdepartments` があれば表示）
4. **学部注釈の表示**（`note` フィールド。オレンジ背景推奨）
5. **卒業必要単位数** (`total_required_credits`)
6. **登録済み単位数**（全学期合計）
7. **カテゴリ別プログレスバー**:
   - 100% 超: 緑
   - 50%以上: オレンジ
   - 50%未満: 赤
8. **表示形式**: `修得単位 / 必要単位 単位`

### Flutter 実装のリファレンス

Flutter 版の実装ファイル:
- `lib/functions/graduation_requirements_service.dart`
  - JSON取得・キャッシュ
  - `CreditCalculator.calculate()` - マッチング・集計ロジック
  - `CategoryProgress` データクラス
- `lib/components/credit_summary.dart`
  - 「単位集計」タブのUIコンポーネント

## データ更新フロー

### 新年度対応（例: 2027年度）

1. 学則PDFを入手（毎年 4/1 ごろ関学から公開）
2. `Syllabus_python/parse_graduation_requirements.py` を実行:
   ```
   python3 parse_graduation_requirements.py \
     /path/to/kwu_rules_20270401.pdf \
     docs/graduation_requirements_2027.json
   ```
3. 目視で確認・手動補正
4. `docs/` と `gh-pages` ブランチにコミット・プッシュ
5. フロントエンドの年度セレクタに2027を追加

### 既知の抽出失敗パターン

- **英名併記の科目**: `English Communication A` など→通常は正しく抽出されるが、
  元PDFの改行位置次第で途切れることあり
- **3階層以上のカテゴリ構造**: 現在は2階層（親-子）まで対応
- **変動単位科目**: `（1科目各1～8単位）` など複数フォーマット対応済み
- **卒業要件のマルチライン**: 修正済みだが、学部により再調整要

## 実装優先度

1. **[必須]** 年度・学部・学科セレクタ
2. **[必須]** カテゴリ別プログレスバー
3. **[必須]** `note` 注釈表示
4. **[推奨]** 全学期合算モード
5. **[推奨]** CSVエクスポート（手動記録用）
6. **[任意]** 学部またぎ科目の複数カテゴリ加算オプション

## 参考: Flutter 版のマッチングコード

```dart
// 科目名正規化
String _normalizeSubjectName(String name) {
  var s = name.trim();
  s = s.replaceAll(RegExp(r'【[0-9]{1,3}】'), '');
  if (s.contains('／')) s = s.split('／').first;
  if (s.contains('/') && !s.startsWith('/')) s = s.split('/').first;
  s = s.replaceAll('　', '').trim();
  return s;
}

// カテゴリを再帰的に走査して {カテゴリ名: {科目名Set}} を構築
void _walkCategories(List categories, Map<String, Set<String>> out) {
  for (final cat in categories) {
    final catName = cat['name'];
    out.putIfAbsent(catName, () => <String>{});
    for (final subj in cat['subjects'] ?? []) {
      out[catName]!.add(_normalizeSubjectName(subj['name']));
    }
    _walkCategories(cat['subcategories'] ?? [], out);
  }
}
```

## 質問窓口

- 元PDFパーサー: `Syllabus_python/parse_graduation_requirements.py`
- 出力データ: `Syllabus_python/docs/graduation_requirements_YYYY.json`
- Flutter 実装: `time_schedule/lib/components/credit_summary.dart`

不明点は Flutter 側の実装を参照してください。
