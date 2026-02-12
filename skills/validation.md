# URL検証実装ガイド

## 概要

URL の形式検証と正規化を担当。`validator.py` に集約。

---

## ファイル構成

```
shortener/
└── validator.py    # URL検証・正規化
```

---

## 実装方針

### 1. 形式チェック: is_valid_url()

```python
import re
from shortener.config import MAX_URL_LENGTH

def is_valid_url(url: str) -> bool:
    """URL形式をチェック。スキームなしでも可。"""
    if not url or not isinstance(url, str):
        return False
    if len(url) > MAX_URL_LENGTH:
        return False
    
    # ドメイン形式のパターン
    pattern = re.compile(
        r"^(https?://)?"                    # スキーム（オプション）
        r"([a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+"  # サブドメイン
        r"[a-zA-Z]{2,}"                     # TLD
        r"(:\d{1,5})?"                      # ポート（オプション）
        r"(/[^\s]*)?$"                      # パス（オプション）
    )
    return bool(pattern.match(url))
```

### 2. スキームチェック: has_valid_scheme()

```python
from shortener.config import ALLOWED_SCHEMES

def has_valid_scheme(url: str) -> bool:
    """許可されたスキームで始まるかチェック。"""
    if not url or not isinstance(url, str):
        return False
    return any(url.startswith(f"{scheme}://") for scheme in ALLOWED_SCHEMES)
```

### 3. 正規化: normalize_url()

```python
def normalize_url(url: str) -> str:
    """URLを正規化: スキーム付与、末尾スラッシュ削除。"""
    if not url:
        return url
    
    url = url.strip()
    
    # スキームがなければ https:// を付与
    if not has_valid_scheme(url):
        url = f"https://{url}"
    
    # 末尾スラッシュ削除（ルートパス以外）
    if url.count("/") > 2 and url.endswith("/"):
        url = url.rstrip("/")
    
    return url
```

### 4. 統合関数: validate_and_normalize()

```python
def validate_and_normalize(url: str) -> tuple:
    """検証と正規化を一括実行。
    
    Returns:
        (normalized_url, None) if valid
        (None, error_message) if invalid
    """
    if not url or not isinstance(url, str):
        return (None, "URL must be a non-empty string")
    
    normalized = normalize_url(url)
    
    # スキームを除いた部分で形式チェック
    url_without_scheme = normalized.replace("https://", "").replace("http://", "")
    if not is_valid_url(url_without_scheme):
        return (None, f"Invalid URL format: {url}")
    
    if len(normalized) > MAX_URL_LENGTH:
        return (None, f"URL exceeds maximum length of {MAX_URL_LENGTH} characters")
    
    return (normalized, None)
```

---

## エッジケース対応

| 入力 | 期待動作 |
|------|---------|
| `""` | エラー |
| `None` | エラー |
| `"example.com"` | `"https://example.com"` に正規化 |
| `"http://example.com/"` | 末尾スラッシュ削除 |
| `"https://example.com"` | そのまま |
| 2048文字超 | エラー |
| `"ftp://example.com"` | エラー（スキーム不許可） |
| `"not a url"` | エラー |

---

## cli.py での使用

```python
from shortener.validator import validate_and_normalize

def cmd_shorten(args):
    normalized, error = validate_and_normalize(args.url)
    if error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
    
    # normalized を使用して処理続行
```

**重要**: cli.py 内で独自の検証ロジックを書かない。必ず `validator.py` を使用。

---

## テストポイント

1. **正常系**: 有効なURL各種
2. **境界値**: 最大長、ちょうど最大長-1
3. **異常系**: 空文字、None、不正形式、長すぎ
4. **正規化**: スキーム付与、末尾スラッシュ削除
