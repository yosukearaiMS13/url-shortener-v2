# テスト戦略ガイド

## 概要

`unittest` を使用した単体テスト + 統合テスト。全モジュール完全カバレッジ。

---

## ファイル構成

```
tests/
├── __init__.py
├── test_validator.py
├── test_hasher.py
├── test_expiry.py
├── test_stats.py
├── test_store.py
└── test_cli.py
```

---

## テスト実行方法

```bash
# 全テスト実行
python -m unittest discover -s tests -v

# 個別モジュール
python -m unittest tests.test_validator -v

# 特定テストケース
python -m unittest tests.test_store.TestShorten.test_creates_entry -v
```

---

## 共通パターン

### 1. テストクラス構造

```python
import unittest
import tempfile
import os

class TestModuleName(unittest.TestCase):
    
    def setUp(self):
        """各テスト前の準備。"""
        # 一時ディレクトリ作成
        self.test_dir = tempfile.mkdtemp()
        os.environ["SHORTENER_DATA_DIR"] = self.test_dir
        
        # 設定を再読み込み（環境変数反映）
        import shortener.config
        shortener.config.DATA_DIR = self.test_dir
        shortener.config.URLS_FILE = os.path.join(self.test_dir, "urls.json")
        shortener.config.STATS_FILE = os.path.join(self.test_dir, "stats.json")
    
    def tearDown(self):
        """各テスト後のクリーンアップ。"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
```

### 2. アサーションパターン

```python
# 値の検証
self.assertEqual(result, expected)
self.assertTrue(condition)
self.assertFalse(condition)
self.assertIsNone(value)
self.assertIsNotNone(value)

# 例外の検証
with self.assertRaises(ValueError) as ctx:
    function_that_raises()
self.assertIn("expected message", str(ctx.exception))

# 型の検証
self.assertIsInstance(result, dict)
```

---

## モジュール別テスト方針

### test_validator.py

```python
class TestIsValidUrl(unittest.TestCase):
    def test_valid_http_url(self):
        self.assertTrue(is_valid_url("http://example.com"))
    
    def test_valid_https_url(self):
        self.assertTrue(is_valid_url("https://example.com"))
    
    def test_url_without_scheme(self):
        self.assertTrue(is_valid_url("example.com"))
    
    def test_empty_string(self):
        self.assertFalse(is_valid_url(""))
    
    def test_none(self):
        self.assertFalse(is_valid_url(None))
    
    def test_exceeds_max_length(self):
        long_url = "https://example.com/" + "a" * 2100
        self.assertFalse(is_valid_url(long_url))


class TestNormalizeUrl(unittest.TestCase):
    def test_adds_https_scheme(self):
        self.assertEqual(normalize_url("example.com"), "https://example.com")
    
    def test_strips_trailing_slash(self):
        self.assertEqual(normalize_url("https://example.com/path/"),
                         "https://example.com/path")
    
    def test_keeps_root_slash(self):
        # https://example.com/ → そのまま（ルートは削除しない？）
        # 仕様確認が必要
        pass
```

### test_hasher.py

```python
class TestGenerateCode(unittest.TestCase):
    def test_deterministic(self):
        url = "https://example.com"
        code1 = generate_code(url)
        code2 = generate_code(url)
        self.assertEqual(code1, code2)
    
    def test_different_urls_different_codes(self):
        code1 = generate_code("https://example1.com")
        code2 = generate_code("https://example2.com")
        self.assertNotEqual(code1, code2)
    
    def test_correct_length(self):
        code = generate_code("https://example.com")
        self.assertEqual(len(code), CODE_LENGTH)
    
    def test_valid_characters(self):
        code = generate_code("https://example.com")
        self.assertTrue(all(c in CODE_CHARSET for c in code))
```

### test_store.py

```python
class TestShorten(unittest.TestCase):
    def test_creates_entry(self):
        result = shorten("https://example.com")
        self.assertIn("code", result)
        self.assertEqual(result["url"], "https://example.com")
    
    def test_duplicate_code_raises(self):
        shorten("https://example.com", custom_code="abc123")
        with self.assertRaises(ValueError):
            shorten("https://other.com", custom_code="abc123")
    
    def test_increments_total_created(self):
        shorten("https://example.com")
        stats = get_stats()
        self.assertEqual(stats["total_created"], 1)


class TestExpand(unittest.TestCase):
    def test_returns_url(self):
        result = shorten("https://example.com")
        url = expand(result["code"])
        self.assertEqual(url, "https://example.com")
    
    def test_not_found_raises(self):
        with self.assertRaises(KeyError):
            expand("nonexistent")
    
    def test_expired_raises(self):
        # 期限切れのエントリを手動作成してテスト
        pass


class TestDelete(unittest.TestCase):
    def test_returns_true_on_success(self):
        result = shorten("https://example.com")
        self.assertTrue(delete(result["code"]))
    
    def test_returns_false_on_not_found(self):
        self.assertFalse(delete("nonexistent"))
    
    def test_increments_total_deleted(self):
        result = shorten("https://example.com")
        delete(result["code"])
        stats = get_stats()
        self.assertEqual(stats["total_deleted"], 1)
```

### test_cli.py（統合テスト）

```python
import subprocess

class TestCli(unittest.TestCase):
    def test_shorten_command(self):
        result = subprocess.run(
            ["python", "-m", "shortener.cli", "shorten", "https://example.com"],
            capture_output=True, text=True, env=self.env
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Shortened:", result.stdout)
    
    def test_invalid_url_exits_with_error(self):
        result = subprocess.run(
            ["python", "-m", "shortener.cli", "shorten", "not-a-url"],
            capture_output=True, text=True, env=self.env
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error:", result.stderr)
    
    def test_help_flag(self):
        result = subprocess.run(
            ["python", "-m", "shortener.cli", "--help"],
            capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage:", result.stdout)
```

---

## テスト時の注意点

1. **環境変数でデータディレクトリを分離** - 本番データを汚染しない
2. **setUp/tearDown で確実にクリーンアップ**
3. **時間依存テストは `unittest.mock.patch` で datetime をモック**
4. **統合テストは subprocess で実行** - 実際のCLI動作を検証

---

## カバレッジ確認

```bash
# coverage パッケージ使用（オプション）
pip install coverage
coverage run -m unittest discover -s tests
coverage report -m
```

目標: **全モジュール 100% ライン/ブランチカバレッジ**
