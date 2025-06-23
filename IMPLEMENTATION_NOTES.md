# Implementation Notes / 実装ノート

This document describes the implementation details of the real estate scraping system.

## Overview / 概要

The system has been implemented with the following components:

### 1. Enhanced Text Parsing (`src/utils/text_parser.py`)

Created a comprehensive Japanese text parser with the following features:

- **Text Normalization**: Converts full-width characters to half-width (e.g., "１２３" → "123")
- **Rent Parsing**: Handles various formats like "8.5万円" → 85000
- **Area Parsing**: Parses square meters from different notations (㎡, m², 平米)
- **Floor Plan Normalization**: Standardizes layouts (e.g., "１ＬＤＫ" → "1LDK")
- **Station Distance**: Extracts walking minutes from text like "徒歩5分" → 5
- **Building Age**: Parses age from "築5年" format
- **Floor Information**: Extracts floor number and total floors
- **Address Components**: Breaks down Japanese addresses into prefecture, city, district

### 2. Robust Robots.txt Parser (`src/utils/robots_parser.py`)

Implemented a proper robots.txt compliance checker:

- Uses Python's `urllib.robotparser` for accurate parsing
- Caches parsed robots.txt per domain to reduce requests
- Supports crawl delay extraction
- Handles missing robots.txt gracefully
- Provides request rate information when available

### 3. HOMES Scraper (`src/scrapers/homes.py`)

Added a complete scraper for HOMES.co.jp:

- Inherits from `BaseScraper` for consistent behavior
- Uses the Japanese text parser for data normalization
- Placeholder selectors ready for actual HTML structure
- Comprehensive error handling
- Extracts all required property fields

### 4. Integration Updates

- Added `pyarrow` dependency for Parquet export support
- Updated SUUMO scraper to use the text parser
- Modified base scraper to use the robust robots parser
- Added both scrapers to the main execution flow

### 5. Example Scripts (`examples/scrape_example.py`)

Created comprehensive examples showing:

- Basic scraping with default settings
- Targeting specific areas and property types
- Exporting to different formats
- Display of available options (areas, property types, etc.)

### 6. Test Suite

Added unit tests for:

- **Text Parser Tests** (`tests/test_text_parser.py`): Comprehensive tests for all parsing functions
- **Robots Parser Tests** (`tests/test_robots_parser.py`): Tests with mocked HTTP responses

## Key Design Decisions / 設計上の重要な決定

### 1. Modular Architecture

- Each scraper inherits from `BaseScraper`
- Utilities are separated into focused modules
- Clear separation between data models, scrapers, and utilities

### 2. Japanese Text Handling

- Proper Unicode normalization (NFKC)
- Handles both full-width and half-width characters
- Robust parsing of Japanese-specific formats

### 3. Rate Limiting and Compliance

- Built-in rate limiting (10 requests/60 seconds)
- Robots.txt checking before scraping
- Respectful delays between requests

### 4. Error Handling

- Comprehensive logging with loguru
- Graceful handling of parsing errors
- Continue on error to maximize data collection

### 5. Data Export Flexibility

- Support for CSV (Excel-compatible with UTF-8 BOM)
- JSON for web applications
- Parquet for big data processing

## Future Improvements / 今後の改善点

1. **Selenium Integration**: Add support for JavaScript-rendered pages
2. **Proxy Support**: Rotate IPs for large-scale scraping
3. **Database Storage**: Direct storage to PostgreSQL/MySQL
4. **API Development**: REST API for scraped data access
5. **Real HTML Selectors**: Update placeholder selectors with actual site structure
6. **Incremental Scraping**: Track already scraped properties
7. **Data Validation**: More robust validation of scraped data
8. **Async Scraping**: Use asyncio for parallel scraping

## Usage Tips / 使用上のヒント

1. **Start Small**: Test with one area and property type first
2. **Monitor Logs**: Check logs directory for detailed information
3. **Respect Limits**: Don't increase rate limits without checking site policies
4. **Data Quality**: Always validate scraped data before analysis
5. **Regular Updates**: Website structures change; update selectors as needed

## Troubleshooting / トラブルシューティング

### Common Issues:

1. **No data scraped**: Check if selectors match current HTML structure
2. **Rate limit errors**: Reduce concurrent requests or increase delays
3. **Parsing errors**: Check logs for specific fields failing
4. **Memory issues**: Process data in batches for large scraping jobs

### Debug Mode:

Set log level to DEBUG in `src/utils/logger.py` for detailed information:
```python
logger.add(sys.stdout, level="DEBUG")
```