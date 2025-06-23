# データ処理機能ドキュメント

このドキュメントでは、スクレイピングしたデータの整形・保存処理機能について説明します。

## 機能概要

### 1. データ正規化

不動産データの表記ゆれを自動的に正規化します：

- **間取り**: `１ＬＤＫ` → `1LDK`, `1LDK+S` → `1LDK`
- **家賃**: `12.5万円` → `125000`, `125,000円` → `125000`
- **面積**: `35.00㎡` → `35.0`, `35m2` → `35.0`
- **駅徒歩**: `徒歩5分` → `5`
- **諸費用**: `なし` → `0`, `1ヶ月` → `1`

### 2. ジオコーディング

住所から緯度経度を自動取得：

- Google Maps API対応（APIキー必要）
- OpenStreetMap Nominatim（無料）へのフォールバック
- 日本国内に特化した設定

### 3. データ品質チェック

- 欠損値の検出とレポート
- 異常値の検出（例：面積0㎡、家賃0円）
- 重複データの検出
- 品質スコア（0-100）の算出

### 4. S3アップロード

- 日付ベースのパス構造（例：`s3://bucket/raw/tokyo/2025/06/23_tokyo.csv`）
- CSV、JSON、Parquet形式対応
- 自動リトライとエラーハンドリング

## 使用方法

### 基本的な使用方法

```bash
# データ処理を含むスクレイピング
python -m src.main --process-data

# ジオコーディングを有効化
python -m src.main --geocode

# S3アップロードを有効化
python -m src.main --upload-s3

# すべての機能を有効化
python -m src.main --geocode --upload-s3
```

### 環境変数の設定

`.env`ファイルに以下を設定：

```env
# Google Maps API（ジオコーディング用）
GOOGLE_MAPS_API_KEY=your_api_key_here

# AWS S3設定
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=ap-northeast-1
S3_BUCKET_NAME=real-estate-data
```

### Pythonコードでの使用

```python
from src.utils import DataExporter
from src.models.property import Property

# プロパティデータのリスト
properties = [...]

# データエクスポーターの初期化
exporter = DataExporter()

# 処理とエクスポート
result = exporter.process_and_export(
    properties,
    export_format="csv",
    apply_geocoding=True,
    upload_to_s3=True
)

print(f"品質スコア: {result['quality_score']}/100")
print(f"処理済みレコード数: {result['records_processed']}")
print(f"S3パス: {result['s3_path']}")
```

## モジュール詳細

### DataProcessor

データ正規化を担当：

```python
from src.utils import DataProcessor

processor = DataProcessor()

# 個別の正規化
floor_plan = processor.normalize_floor_plan("１ＬＤＫ")  # → "1LDK"
rent = processor.normalize_rent("12.5万円")  # → 125000
area = processor.normalize_area("35.00㎡")  # → 35.0

# DataFrameの一括処理
df = processor.process_dataframe(df)
```

### Geocoder

住所のジオコーディング：

```python
from src.utils import Geocoder

# Google Maps API使用
geocoder = Geocoder(provider="google")

# 無料のNominatim使用
geocoder = Geocoder(provider="nominatim")

# 単一住所のジオコーディング
lat, lon = geocoder.geocode("東京都渋谷区恵比寿1-2-3")

# バッチ処理
results = geocoder.batch_geocode(addresses)
```

### DataQualityChecker

データ品質の検証：

```python
from src.utils import DataQualityChecker

checker = DataQualityChecker()

# 品質チェック
report = checker.check_data_quality(df)
print(f"品質スコア: {report['quality_score']}")

# 自動修正
fixed_df = checker.fix_common_issues(df)
```

## 出力例

### 品質レポート

```json
{
  "total_records": 1000,
  "quality_score": 92.5,
  "missing_values": {
    "station_distance": {
      "count": 50,
      "percentage": 5.0
    }
  },
  "outliers": {
    "rent": [
      {
        "index": 234,
        "value": 5500000,
        "issue": "Above maximum (5000000)",
        "property_id": "suumo_12345"
      }
    ]
  },
  "duplicates": {
    "property_id": {
      "count": 2,
      "examples": {
        "suumo_999": 2
      }
    }
  }
}
```

### S3パス構造

```
s3://real-estate-data/
├── raw/
│   ├── tokyo/
│   │   ├── 2025/
│   │   │   ├── 06/
│   │   │   │   ├── 23_tokyo.csv
│   │   │   │   ├── 23_tokyo.parquet
│   │   │   │   └── 23_tokyo.json
```

## トラブルシューティング

### ジオコーディングが動作しない

1. APIキーが正しく設定されているか確認
2. `googlemaps`ライブラリがインストールされているか確認
3. インターネット接続を確認

### S3アップロードが失敗する

1. AWS認証情報が正しく設定されているか確認
2. S3バケットが存在し、書き込み権限があるか確認
3. `boto3`ライブラリがインストールされているか確認

### メモリ不足エラー

大量のデータを処理する場合：

```python
# バッチ処理で分割
batch_size = 1000
for i in range(0, len(properties), batch_size):
    batch = properties[i:i+batch_size]
    result = exporter.process_and_export(batch)
```