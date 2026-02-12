# URL Shortener CLI v2

長いURLを短縮コードに変換するコマンドラインツール。

## 特徴

- 🔗 URLを6文字の短縮コードに変換
- ⏰ URL有効期限の設定が可能
- 📊 使用統計の追跡
- 🧹 期限切れURLの一括削除
- 📦 Python標準ライブラリのみ使用（外部依存なし）

## 要件

- Python 3.8+

## インストール

```bash
git clone https://github.com/yosukearaiMS13/url-shortener-v2.git
cd url-shortener-v2
```

## 使い方

```bash
# URLを短縮
python -m shortener.cli shorten https://example.com/very/long/url

# カスタムコードで短縮
python -m shortener.cli shorten https://example.com --code mycode

# 24時間で期限切れに設定
python -m shortener.cli shorten https://example.com --expires 24

# 短縮コードから元URLを取得
python -m shortener.cli expand abc123

# 短縮URLの詳細を表示
python -m shortener.cli info abc123

# 全URLを一覧表示
python -m shortener.cli list

# 期限切れも含めて一覧表示
python -m shortener.cli list --include-expired

# 短縮URLを削除
python -m shortener.cli delete abc123

# 使用統計を表示
python -m shortener.cli stats

# 期限切れURLを一括削除
python -m shortener.cli cleanup

# 削除対象の確認のみ（実際には削除しない）
python -m shortener.cli cleanup --dry-run
```

## プロジェクト構成

```
url-shortener-v2/
├── README.md
├── docs/
│   └── plan.md              # 仕様書（何を作るか）
├── skills/
│   ├── cli-implementation.md    # CLI実装ガイド
│   ├── data-access.md           # データアクセス実装ガイド
│   ├── validation.md            # URL検証実装ガイド
│   ├── hashing.md               # コード生成実装ガイド
│   ├── expiry.md                # 有効期限実装ガイド
│   └── testing.md               # テスト戦略ガイド
├── shortener/                   # ソースコード（実装予定）
│   ├── __init__.py
│   ├── cli.py
│   ├── store.py
│   ├── hasher.py
│   ├── validator.py
│   ├── stats.py
│   ├── expiry.py
│   └── config.py
└── tests/                       # テストコード（実装予定）
    ├── test_cli.py
    ├── test_store.py
    ├── test_hasher.py
    ├── test_validator.py
    ├── test_stats.py
    └── test_expiry.py
```

## データ保存

URLと統計情報はJSONファイルに保存されます：

- `urls.json` — 短縮URL一覧
- `stats.json` — 使用統計

保存先は環境変数で変更可能：

```bash
export SHORTENER_DATA_DIR=/path/to/data
```

## テスト実行

```bash
python -m unittest discover -s tests -v
```

## ドキュメント

| ドキュメント | 内容 |
|-------------|------|
| [docs/plan.md](docs/plan.md) | 仕様書 — コマンド、API、データモデル、テスト仕様 |
| [skills/](skills/) | 実装ガイド — 各モジュールの実装方法 |

## ライセンス

MIT License
