# URL Shortener CLI v2 — 仕様書

## 概要

URL短縮CLIアプリケーション。長いURLを短縮コードに変換し、管理・展開する。

| 項目 | 値 |
|------|-----|
| 言語 | Python 3.8+ |
| 依存関係 | 標準ライブラリのみ |
| 実行方法 | `python -m shortener.cli <command>` |

---

## 1. コマンド一覧

| コマンド | 説明 | 引数 | オプション |
|----------|------|------|------------|
| `shorten <url>` | URLを短縮コードに変換 | `url`: 短縮対象URL | `--code`: カスタムコード<br>`--expires`: 有効期限（時間） |
| `expand <code>` | 短縮コードから元URLを取得 | `code`: 短縮コード | - |
| `delete <code>` | 短縮URLを削除 | `code`: 短縮コード | - |
| `list` | 全URLを一覧表示 | - | `--include-expired`: 期限切れも表示 |
| `stats` | 使用統計を表示 | - | - |
| `info <code>` | 短縮URLの詳細情報を表示 | `code`: 短縮コード | - |
| `cleanup` | 期限切れURLを一括削除 | - | `--dry-run`: 削除対象の確認のみ |

---

## 2. モジュール一覧

| モジュール | 責務 |
|-----------|------|
| `cli.py` | CLIエントリーポイント、引数解析、出力 |
| `store.py` | URL永続化、CRUD操作 |
| `hasher.py` | 短縮コード生成 |
| `validator.py` | URL検証・正規化 |
| `stats.py` | 統計情報管理 |
| `expiry.py` | 有効期限計算・判定 |
| `config.py` | 設定値定義 |

---

## 3. 関数インターフェース一覧

### 3.1 validator.py

| 関数 | 引数 | 戻り値 | 説明 |
|------|------|--------|------|
| `is_valid_url(url)` | `url: str` | `bool` | URL形式チェック |
| `has_valid_scheme(url)` | `url: str` | `bool` | スキームチェック |
| `normalize_url(url)` | `url: str` | `str` | URL正規化 |
| `validate_and_normalize(url)` | `url: str` | `tuple[str\|None, str\|None]` | 検証+正規化 |

### 3.2 hasher.py

| 関数 | 引数 | 戻り値 | 説明 |
|------|------|--------|------|
| `generate_code(url, length)` | `url: str, length: int` | `str` | URL→短縮コード生成 |
| `generate_random_code(length)` | `length: int` | `str` | ランダムコード生成 |
| `is_valid_code(code)` | `code: str` | `bool` | コード形式検証 |

### 3.3 expiry.py

| 関数 | 引数 | 戻り値 | 説明 |
|------|------|--------|------|
| `calculate_expiry(hours)` | `hours: int` | `str\|None` | 有効期限タイムスタンプ計算 |
| `is_expired(expires_at)` | `expires_at: str\|None` | `bool` | 有効期限切れ判定 |
| `get_remaining_time(expires_at)` | `expires_at: str\|None` | `timedelta\|None` | 残り時間取得 |
| `format_remaining(expires_at)` | `expires_at: str\|None` | `str` | 残り時間フォーマット |

### 3.4 store.py

| 関数 | 引数 | 戻り値 | 説明 |
|------|------|--------|------|
| `shorten(url, custom_code, expiry_hours)` | `url: str, custom_code: str\|None, expiry_hours: int` | `dict` | URL登録 |
| `expand(code)` | `code: str` | `str` | コード→URL取得 |
| `delete(code)` | `code: str` | `bool` | 削除 |
| `list_all(include_expired)` | `include_expired: bool` | `list[dict]` | 全エントリ取得 |
| `get_entry(code)` | `code: str` | `dict` | 単一エントリ取得 |
| `count(include_expired)` | `include_expired: bool` | `int` | エントリ数 |
| `cleanup_expired()` | - | `int` | 期限切れ削除 |

### 3.5 stats.py

| 関数 | 引数 | 戻り値 | 説明 |
|------|------|--------|------|
| `get_stats()` | - | `dict` | 統計情報取得 |
| `get_summary()` | - | `str` | 人間可読サマリー |
| `increment_stat(key)` | `key: str` | `None` | 統計インクリメント |
| `reset_stats()` | - | `None` | 統計リセット |

---

## 4. データモデル一覧

### 4.1 urls.json

URL永続化ファイル。キーは短縮コード。

```json
{
  "abc123": {
    "url": "https://example.com/long-url",
    "created_at": "2026-02-12T09:00:00+00:00",
    "expires_at": "2026-02-13T09:00:00+00:00",
    "access_count": 5
  }
}
```

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `url` | string | 元のURL |
| `created_at` | string (ISO8601) | 作成日時 |
| `expires_at` | string (ISO8601) \| null | 有効期限（nullは無期限） |
| `access_count` | integer | アクセス回数 |

### 4.2 stats.json

統計情報ファイル。

```json
{
  "total_created": 10,
  "total_deleted": 3,
  "total_expanded": 25,
  "total_expired": 2
}
```

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `total_created` | integer | 累計作成数 |
| `total_deleted` | integer | 累計削除数 |
| `total_expanded` | integer | 累計展開回数 |
| `total_expired` | integer | 累計期限切れ削除数 |

---

## 5. 設定値一覧

| 定数 | 型 | デフォルト値 | 説明 |
|------|-----|-------------|------|
| `DATA_DIR` | str | `.` | データ保存ディレクトリ |
| `URLS_FILE` | str | `{DATA_DIR}/urls.json` | URL保存ファイル |
| `STATS_FILE` | str | `{DATA_DIR}/stats.json` | 統計ファイル |
| `CODE_LENGTH` | int | `6` | 短縮コードの長さ |
| `CODE_CHARSET` | str | `a-z0-9` | 使用可能文字 |
| `MAX_URL_LENGTH` | int | `2048` | 最大URL長 |
| `ALLOWED_SCHEMES` | tuple | `("http", "https")` | 許可スキーム |
| `DEFAULT_EXPIRY_HOURS` | int | `0` | デフォルト有効期限（0=無期限） |

---

## 6. エラー仕様

| エラー種別 | 例外 | メッセージ例 |
|-----------|------|-------------|
| URL形式不正 | `ValueError` | `"Invalid URL format: xxx"` |
| コード重複 | `ValueError` | `"Short code 'xxx' already exists"` |
| コード未存在 | `KeyError` | `"Short code 'xxx' not found"` |
| URL期限切れ | `KeyError` | `"Short code 'xxx' has expired"` |

---

## 7. テスト仕様

### 7.1 テストファイル一覧

| テストファイル | 対象モジュール |
|---------------|---------------|
| `test_validator.py` | `validator.py` |
| `test_hasher.py` | `hasher.py` |
| `test_expiry.py` | `expiry.py` |
| `test_stats.py` | `stats.py` |
| `test_store.py` | `store.py` |
| `test_cli.py` | `cli.py` |

### 7.2 テストケース概要

#### test_validator.py
- 有効なURL（http/https）が `True` を返す
- 無効なURL（スキームなし、不正形式）が `False` を返す
- 長すぎるURLが拒否される
- `normalize_url` がスキームを付与する
- `normalize_url` が末尾スラッシュを削除する

#### test_hasher.py
- 同じURLは同じコードを生成する（決定性）
- 異なるURLは異なるコードを生成する
- コード長が `CODE_LENGTH` と一致する
- コードが `CODE_CHARSET` 内の文字のみで構成される
- `is_valid_code` が正しく検証する

#### test_expiry.py
- `hours=0` で `None` を返す
- `hours>0` で未来のタイムスタンプを返す
- 過去の `expires_at` は `is_expired=True`
- 未来の `expires_at` は `is_expired=False`
- `None` は `is_expired=False`（無期限）
- `format_remaining` が人間可読形式を返す

#### test_stats.py
- 初期状態で全カウンタが0
- `increment_stat` がカウンタを増加させる
- `reset_stats` が全カウンタをリセットする
- `get_summary` が文字列を返す

#### test_store.py
- `shorten` が新しいエントリを作成する
- `shorten` で重複コードが `ValueError` を発生させる
- `expand` が正しいURLを返す
- `expand` が存在しないコードで `KeyError` を発生させる
- `expand` が期限切れコードで `KeyError` を発生させる
- `expand` が `access_count` を増加させる
- `delete` が成功時に `True`、失敗時に `False` を返す
- `delete` が `total_deleted` を増加させる
- `list_all` が全エントリを返す
- `cleanup_expired` が期限切れエントリを削除する

#### test_cli.py
- 各サブコマンドが正しく動作する（subprocess経由）
- 不正な入力でエラーメッセージと終了コード1
- `--help` がヘルプを表示する
