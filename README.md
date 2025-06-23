# Real Estate Scraping Project / 不動産スクレイピングプロジェクト

This project scrapes real estate data from major Japanese property portals for data analysis and visualization.

## 🎯 Purpose / 目的

To gain practical experience in data engineering and data analysis through the complete process of scraping, analyzing, and visualizing real estate data.

不動産のスクレイピングから分析・可視化までを一通り実施し、データエンジニアリング・データ分析スキルを実践的に習得する。

## 📋 Features / 機能

- Scrape property listings from major real estate portals (SUUMO, HOMES)
- Target: Tokyo 23 wards rental properties
- Data export in multiple formats (CSV, JSON, Parquet)
- Data normalization and quality checks
- Geocoding support (Google Maps API or free Nominatim)
- AWS S3 upload integration
- Rate limiting and respectful scraping
- Comprehensive logging with loguru
- Modular architecture for easy extension

## 🚀 Quick Start / クイックスタート

### Prerequisites / 前提条件

- Python 3.12+
- pip

### Installation / インストール

```bash
# Clone the repository
git clone https://github.com/kawafuchieirin/real-estate-scraping.git
cd real-estate-scraping

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage / 基本的な使い方

```bash
# Run with default settings (first 3 areas, all property types)
python -m src.main

# Specify areas and property types
python -m src.main --areas 13113 13104 --property-types apartment

# Export as different formats
python -m src.main --export-format json
python -m src.main --export-format parquet

# Limit pages per search
python -m src.main --max-pages 3

# Skip data processing (raw data only)
python -m src.main --skip-processing

# Enable geocoding (requires API key setup)
python -m src.main --geocode

# Upload to S3 (requires AWS credentials)
python -m src.main --upload-s3

# Full example with all features
python -m src.main --sites SUUMO HOMES --areas 13113 --geocode --upload-s3
```

### Command Line Options / コマンドラインオプション

| Option | Description | Default |
|--------|-------------|--------|
| `--sites` | Sites to scrape (SUUMO, HOMES) | All sites |
| `--areas` | Area codes to scrape (e.g., 13113 for Shibuya) | First 3 areas |
| `--property-types` | Property types (apartment, apart, house) | All types |
| `--max-pages` | Maximum pages per search | 5 |
| `--export-format` | Export format (csv, json, parquet) | csv |
| `--skip-processing` | Skip data normalization and quality checks | False |
| `--geocode` | Enable address geocoding | False |
| `--upload-s3` | Upload results to AWS S3 | False |

## 📁 Project Structure / プロジェクト構造

```
real-estate-scraping/
├── src/
│   ├── config/          # Configuration settings
│   ├── scrapers/        # Website scrapers
│   ├── models/          # Data models
│   ├── utils/           # Utility functions
│   └── main.py          # Main entry point
├── data/
│   ├── raw/            # Raw scraped data
│   └── processed/      # Processed data
├── logs/               # Log files
├── tests/              # Test files
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## ⚙️ Configuration / 設定

The project uses the following default settings:

- **Target Areas**: Tokyo 23 wards (東京23区)
- **Property Types**: Apartments (マンション), Apart (アパート), Houses (一戸建て)
- **Rate Limiting**: 10 requests per 60 seconds
- **Export Formats**: CSV, JSON, Parquet

Settings can be modified in `src/config/settings.py`.

### Environment Variables / 環境変数

For advanced features, create a `.env` file:

```bash
# Geocoding (optional)
GOOGLE_MAPS_API_KEY=your_api_key_here

# AWS S3 Upload (optional)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=ap-northeast-1
S3_BUCKET_NAME=your-bucket-name
```

## 📊 Data Fields / データフィールド

Scraped properties include:

- **Basic info**: ID, URL, title, type
- **Location**: Prefecture, city, address, coordinates (with geocoding)
- **Price**: Rent, management fee, deposit, key money
- **Specifications**: Floor plan, area, floor, building age
- **Transportation**: Nearest station, walking distance
- **Features**: Amenities and equipment
- **Metadata**: Scraping timestamp

### Data Processing Features / データ処理機能

When processing is enabled (default), the system automatically:

- **Normalizes Japanese text**: Converts full-width to half-width characters
- **Standardizes formats**: 
  - Floor plans: `１ＬＤＫ` → `1LDK`
  - Rent: `12.5万円` → `125000`
  - Area: `35.00㎡` → `35.0`
- **Validates data quality**: Detects missing values, outliers, duplicates
- **Generates quality score**: 0-100 score for data completeness
- **Geocodes addresses**: Converts addresses to latitude/longitude (optional)

## 🛠️ Development / 開発

### Adding New Scrapers / 新しいスクレイパーの追加

1. Create a new file in `src/scrapers/`
2. Inherit from `BaseScraper`
3. Implement required methods
4. Add to the scrapers dictionary in `main.py`

### Running Tests / テストの実行

```bash
pytest tests/
```

### Code Quality / コード品質

```bash
# Format code
black src/

# Check linting
flake8 src/

# Type checking
mypy src/
```

## ⚠️ Important Notes / 重要な注意事項

1. **Respect robots.txt**: Always check and follow website scraping policies
2. **Rate Limiting**: Built-in rate limiting prevents overwhelming target servers
3. **Legal Compliance**: Ensure compliance with website terms of service
4. **Data Privacy**: Handle scraped data responsibly

## 🗺️ Roadmap / ロードマップ

- [x] Step 1: Basic scraping implementation
- [ ] Step 2: Full scraping implementation for multiple sites
- [ ] Step 3: Data cleaning and normalization
- [ ] Step 4: AWS integration (S3, Glue, Athena)
- [ ] Step 5: Data visualization (QuickSight)
- [ ] Step 6: Machine learning models

## 📄 License / ライセンス

This project is for educational purposes. Please ensure compliance with all relevant laws and website terms of service when using.

## 🤝 Contributing / コントリビューション

Contributions are welcome! Please feel free to submit a Pull Request
