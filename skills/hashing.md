# コード生成実装ガイド

## 概要

短縮コードの生成と検証を担当。`hasher.py` が実装。

---

## ファイル構成

```
shortener/
└── hasher.py    # 短縮コード生成・検証
```

---

## 実装方針

### 1. 決定的コード生成: generate_code()

同じURLは常に同じコードを生成（キャッシュ効率、重複検出に有利）。

```python
import hashlib
from shortener.config import CODE_LENGTH, CODE_CHARSET

def generate_code(url: str, length: int = CODE_LENGTH) -> str:
    """URLからSHA256ベースの短縮コードを生成。決定的。"""
    hash_bytes = hashlib.sha256(url.encode("utf-8")).digest()
    
    code = []
    for i in range(length):
        idx = hash_bytes[i] % len(CODE_CHARSET)
        code.append(CODE_CHARSET[idx])
    
    return "".join(code)
```

### 2. ランダムコード生成: generate_random_code()

カスタムコードが必要な場合やコリジョン回避用。

```python
import random

def generate_random_code(length: int = CODE_LENGTH) -> str:
    """ランダムな短縮コードを生成。"""
    return "".join(random.choices(CODE_CHARSET, k=length))
```

### 3. コード検証: is_valid_code()

```python
def is_valid_code(code: str) -> bool:
    """コードが有効な形式かチェック。"""
    if not code or not isinstance(code, str):
        return False
    if len(code) != CODE_LENGTH:
        return False
    return all(c in CODE_CHARSET for c in code)
```

---

## 設定値

| 定数 | 値 | 説明 |
|------|-----|------|
| `CODE_LENGTH` | `6` | コード長 |
| `CODE_CHARSET` | `"abcdefghijklmnopqrstuvwxyz0123456789"` | 使用文字 |

### 組み合わせ数

- 36文字 × 6桁 = 36^6 = **2,176,782,336** 通り
- 実用上十分なユニーク性

---

## コリジョン対策

ハッシュベースのため異なるURLで同じコードが生成される可能性あり。

```python
# store.py での対策
def shorten(url: str, custom_code: str = None, expiry_hours: int = 0) -> dict:
    urls = _read_urls()
    code = custom_code or generate_code(url)
    
    # コリジョン検出
    if code in urls:
        # 同じURLならOK（冪等性）
        if urls[code]["url"] == url:
            return {"code": code, **urls[code]}
        # 異なるURLなら例外
        raise ValueError(f"Short code '{code}' already exists")
    
    # ... 以下登録処理
```

---

## カスタムコード対応

ユーザー指定のコードは `is_valid_code()` でフォーマット検証。

```python
# cli.py
def cmd_shorten(args):
    if args.code and not is_valid_code(args.code):
        print(f"Error: Invalid code format. Must be {CODE_LENGTH} characters "
              f"using only: {CODE_CHARSET}", file=sys.stderr)
        sys.exit(1)
```

---

## テストポイント

1. **決定性**: 同じURL → 同じコード
2. **一意性**: 異なるURL → 異なるコード（高確率）
3. **フォーマット**: 長さ、文字種
4. **検証**: 有効/無効コードの判定
