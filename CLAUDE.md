# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a real estate scraping repository (不動産スクレイピングのリポジトリ) that scrapes property listings from major Japanese real estate portals for data analysis and visualization.

## Development Status

The project now has:
- **Technology Stack**: Python 3.12+ with BeautifulSoup, Requests, and Selenium
- **Project Structure**: Modular architecture with scrapers, models, utils, and config
- **Dependencies**: Defined in requirements.txt
- **Data Models**: Pydantic models for property data
- **Base Implementation**: SUUMO scraper (placeholder implementation)

## Architecture

```
src/
├── config/          # Configuration and settings
├── scrapers/        # Website-specific scrapers (inherit from BaseScraper)
├── models/          # Pydantic data models
├── utils/           # Utilities (logging, data export)
└── main.py          # Entry point
```

## Commands

### Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Scraper
```bash
# Basic usage (scrapes first 3 areas)
python -m src.main

# Specify areas and property types
python -m src.main --areas 13113 13104 --property-types apartment

# Export as different formats
python -m src.main --export-format json
python -m src.main --export-format parquet
```

### Development
```bash
# Code formatting
black src/

# Linting
flake8 src/

# Type checking
mypy src/

# Run tests
pytest tests/
```

## Important Implementation Notes

1. **Rate Limiting**: Implemented using the `ratelimit` library (10 requests/60 seconds)
2. **Robots.txt Compliance**: Check before scraping each site
3. **Error Handling**: Comprehensive logging with loguru
4. **Data Export**: Supports CSV, JSON, and Parquet formats
5. **Japanese Text**: Ensure proper encoding (UTF-8) for Japanese characters

## Adding New Scrapers

1. Create a new file in `src/scrapers/` (e.g., `homes.py`)
2. Inherit from `BaseScraper`
3. Implement abstract methods:
   - `search_properties()`
   - `parse_property_list()`
   - `parse_property_details()`
4. Add to scrapers dictionary in `main.py`

## Configuration

Key settings in `src/config/settings.py`:
- Target sites configuration
- Tokyo 23 wards area codes
- Property types (apartment, apart, house)
- Rate limiting parameters
- Storage directories

## Next Steps

1. **Complete SUUMO Scraper**: Replace placeholder selectors with actual HTML structure
2. **Add HOMES Scraper**: Implement scraper for homes.co.jp
3. **Data Validation**: Add more robust data validation and cleaning
4. **AWS Integration**: Prepare for S3, Glue, Athena integration
5. **Testing**: Add comprehensive unit and integration tests