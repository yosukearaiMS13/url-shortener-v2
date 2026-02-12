# データアクセス実装ガイド

## 概要

JSON ファイルベースの永続化層。`store.py` と `stats.py` が担当。

---

## ファイル構成

```
shortener/
├── store.py    # URL CRUD操作
├── stats.py    # 統計情報管理
└── config.py   # ファイルパス設定
```

---

## ストレージ設計

### ファイル配置

| ファイル | 用途 | デフォルトパス |
|---------|------|---------------|
| `urls.json` | URL永続化 | `./urls.json` |
| `stats.json` | 統計情報 | `./stats.json` |

環境変数 `SHORTENER_DATA_DIR` でディレクトリ変更可能。

---

## store.py 実装方針

### 1. 読み書きヘルパー

```python
def _read_urls() -> dict:
    """URL mapping ファイルを読み込む。存在しなければ空dict。"""
    if not os.path.exists(URLS_FILE):
        return {}
    try:
        with open(URLS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def _write_urls(data: dict) -> None:
    """URL mapping ファイルに書き込む。"""
    with open(URLS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
```

### 2. CRUD操作

#### Create: shorten()

```python
def shorten(url: str, custom_code: str = None, expiry_hours: int = 0) -> dict:
    urls = _read_urls()
    code = custom_code or generate_code(url)
    
    if code in urls:
        raise ValueError(f"Short code '{code}' already exists")
    
    entry = {
        "url": url,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": calculate_expiry(expiry_hours),
        "access_count": 0,
    }
    urls[code] = entry
    _write_urls(urls)
    
    increment_stat("total_created")  # 統計連携
    
    return {"code": code, **entry}
```

#### Read: expand()

```python
def expand(code: str) -> str:
    urls = _read_urls()
    if code not in urls:
        raise KeyError(f"Short code '{code}' not found")
    
    entry = urls[code]
    
    # 有効期限チェック
    if is_expired(entry.get("expires_at")):
        raise KeyError(f"Short code '{code}' has expired")
    
    # アクセスカウント更新
    entry["access_count"] = entry.get("access_count", 0) + 1
    _write_urls(urls)
    
    increment_stat("total_expanded")
    
    return entry["url"]
```

#### Delete: delete()

```python
def delete(code: str) -> bool:
    urls = _read_urls()
    if code not in urls:
        return False
    
    del urls[code]
    _write_urls(urls)
    
    increment_stat("total_deleted")  # ← 現行アプリのバグ修正ポイント
    
    return True
```

#### Cleanup: cleanup_expired()

```python
def cleanup_expired() -> int:
    urls = _read_urls()
    expired_codes = [
        code for code, entry in urls.items()
        if is_expired(entry.get("expires_at"))
    ]
    
    for code in expired_codes:
        del urls[code]
    
    if expired_codes:
        _write_urls(urls)
        # 一括でカウント更新
        stats = _read_stats()
        stats["total_expired"] = stats.get("total_expired", 0) + len(expired_codes)
        _write_stats(stats)
    
    return len(expired_codes)
```

---

## stats.py 実装方針

### 1. 統計構造

```python
DEFAULT_STATS = {
    "total_created": 0,
    "total_deleted": 0,
    "total_expanded": 0,
    "total_expired": 0,
}
```

### 2. 統計取得

```python
def get_stats() -> dict:
    stats = _read_stats()
    return {
        **stats,
        "active_urls": count(include_expired=False),  # 実際のカウント
    }
```

### 3. インクリメント

```python
def increment_stat(key: str) -> None:
    stats = _read_stats()
    stats[key] = stats.get(key, 0) + 1
    _write_stats(stats)
```

---

## トランザクション考慮

- 単一ファイル操作は原子性なし（教育用のためシンプル化）
- 実運用では `fcntl.flock` やファイルロックを検討
- stats.py と store.py の整合性は「ベストエフォート」

---

## エラーハンドリング

| 状況 | 対応 |
|------|------|
| ファイル不在 | 空データで継続 |
| JSON破損 | 空データで継続、警告ログ |
| 書き込み失敗 | 例外を上位に伝播 |

---

## テスト時の考慮

- テスト用の一時ディレクトリを `DATA_DIR` に設定
- `setUp` で `reset_stats()` を呼び出し
- `tearDown` で一時ファイル削除
