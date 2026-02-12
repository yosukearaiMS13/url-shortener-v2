# 有効期限実装ガイド

## 概要

URL の有効期限計算と判定を担当。`expiry.py` が実装（新規追加モジュール）。

---

## ファイル構成

```
shortener/
└── expiry.py    # 有効期限計算・判定
```

---

## 実装方針

### 1. 有効期限計算: calculate_expiry()

```python
from datetime import datetime, timezone, timedelta

def calculate_expiry(hours: int) -> str | None:
    """指定時間後のISO8601タイムスタンプを返す。
    
    Args:
        hours: 有効期限までの時間。0は無期限。
    
    Returns:
        ISO8601形式のタイムスタンプ、または None（無期限）
    """
    if hours <= 0:
        return None
    
    expiry_time = datetime.now(timezone.utc) + timedelta(hours=hours)
    return expiry_time.isoformat()
```

### 2. 期限切れ判定: is_expired()

```python
def is_expired(expires_at: str | None) -> bool:
    """有効期限切れかどうかを判定。
    
    Args:
        expires_at: ISO8601タイムスタンプ、または None（無期限）
    
    Returns:
        期限切れなら True、有効または無期限なら False
    """
    if expires_at is None:
        return False  # 無期限は期限切れにならない
    
    try:
        expiry_time = datetime.fromisoformat(expires_at)
        return datetime.now(timezone.utc) > expiry_time
    except ValueError:
        return False  # パース失敗は期限切れ扱いしない
```

### 3. 残り時間取得: get_remaining_time()

```python
def get_remaining_time(expires_at: str | None) -> timedelta | None:
    """有効期限までの残り時間を取得。
    
    Returns:
        残り時間の timedelta、期限切れまたは無期限なら None
    """
    if expires_at is None:
        return None
    
    try:
        expiry_time = datetime.fromisoformat(expires_at)
        remaining = expiry_time - datetime.now(timezone.utc)
        if remaining.total_seconds() <= 0:
            return None
        return remaining
    except ValueError:
        return None
```

### 4. 人間可読フォーマット: format_remaining()

```python
def format_remaining(expires_at: str | None) -> str:
    """残り時間を人間可読形式でフォーマット。
    
    Examples:
        "2h 30m"
        "45m"
        "expired"
        "never"
    """
    if expires_at is None:
        return "never"
    
    remaining = get_remaining_time(expires_at)
    if remaining is None:
        return "expired"
    
    total_seconds = int(remaining.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes = remainder // 60
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m"
    else:
        return "<1m"
```

---

## 使用例

### store.py での登録時

```python
from shortener.expiry import calculate_expiry

def shorten(url: str, custom_code: str = None, expiry_hours: int = 0) -> dict:
    entry = {
        "url": url,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": calculate_expiry(expiry_hours),  # ← ここで使用
        "access_count": 0,
    }
```

### store.py での展開時

```python
from shortener.expiry import is_expired

def expand(code: str) -> str:
    entry = urls[code]
    
    if is_expired(entry.get("expires_at")):
        raise KeyError(f"Short code '{code}' has expired")
```

### cli.py での表示時

```python
from shortener.expiry import format_remaining

def cmd_list(args):
    for entry in entries:
        expires = format_remaining(entry.get("expires_at"))
        print(f"  {entry['code']}  →  {entry['url']}  (expires: {expires})")
```

---

## タイムゾーン考慮

- 内部では常に **UTC** を使用
- `datetime.now(timezone.utc)` で現在時刻取得
- ISO8601形式でタイムゾーン情報を保持

---

## テストポイント

1. **calculate_expiry(0)** → `None`
2. **calculate_expiry(24)** → 24時間後のタイムスタンプ
3. **is_expired(過去)** → `True`
4. **is_expired(未来)** → `False`
5. **is_expired(None)** → `False`
6. **format_remaining** の各パターン
