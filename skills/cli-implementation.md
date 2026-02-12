# CLI実装ガイド

## 概要

`argparse` を使用したサブコマンド形式のCLI実装。

---

## ファイル構成

```
shortener/
└── cli.py    # CLIエントリーポイント
```

---

## 実装方針

### 1. エントリーポイント

```python
if __name__ == "__main__":
    main()
```

`python -m shortener.cli` で実行可能にする。

### 2. argparse構成

```python
def main():
    parser = argparse.ArgumentParser(
        prog="shortener",
        description="URL Shortener CLI"
    )
    subparsers = parser.add_subparsers(dest="command")
    
    # 各サブコマンドを登録
    _setup_shorten(subparsers)
    _setup_expand(subparsers)
    _setup_delete(subparsers)
    _setup_list(subparsers)
    _setup_stats(subparsers)
    _setup_info(subparsers)
    _setup_cleanup(subparsers)
    
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    args.func(args)
```

### 3. サブコマンド登録パターン

```python
def _setup_shorten(subparsers):
    p = subparsers.add_parser("shorten", help="Shorten a URL")
    p.add_argument("url", help="URL to shorten")
    p.add_argument("--code", help="Custom short code")
    p.add_argument("--expires", type=int, default=0,
                   help="Expiry time in hours (0=never)")
    p.set_defaults(func=cmd_shorten)
```

### 4. コマンドハンドラパターン

```python
def cmd_shorten(args):
    """Handle 'shorten' subcommand."""
    # 1. 入力検証（validator.py を使用）
    normalized, error = validate_and_normalize(args.url)
    if error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
    
    # 2. ビジネスロジック実行（store.py を使用）
    try:
        result = shorten(normalized, custom_code=args.code,
                         expiry_hours=args.expires)
        print(f"Shortened: {result['code']} → {result['url']}")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
```

---

## 出力フォーマット

### 成功時（stdout）

```
Shortened: abc123 → https://example.com
Expanded: abc123 → https://example.com
Deleted: abc123
```

### 一覧表示

```
  abc123  →  https://example.com  (accessed: 5)
  def456  →  https://other.com    (accessed: 2, expires: 2h 30m)

Total: 2 URLs
```

### エラー時（stderr）

```
Error: Invalid URL format: not-a-url
Error: Short code 'abc123' not found
```

---

## 依存モジュール

| インポート | 用途 |
|-----------|------|
| `argparse` | 引数解析 |
| `sys` | 終了コード、stderr出力 |
| `shortener.store` | CRUD操作 |
| `shortener.stats` | 統計取得 |
| `shortener.validator` | URL検証（validator.pyに統一） |
| `shortener.expiry` | 有効期限フォーマット |

---

## 注意点

- URL検証は `validator.py` のみを使用し、cli.py内での重複実装を避ける
- 例外は適切にキャッチし、ユーザーフレンドリーなメッセージに変換
- 終了コード: 成功=0、エラー=1
