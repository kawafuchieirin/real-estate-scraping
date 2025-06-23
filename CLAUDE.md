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
- **Scrapers**: SUUMO and HOMES scrapers (placeholder implementations)
- **Data Processing**: Automatic normalization, quality checks, and geocoding
- **Export Options**: CSV, JSON, Parquet with optional S3 upload

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
# Basic usage (scrapes first 3 areas with data processing)
python -m src.main

# Specify areas and property types
python -m src.main --areas 13113 13104 --property-types apartment

# Export as different formats
python -m src.main --export-format json
python -m src.main --export-format parquet

# Skip data processing (raw data only)
python -m src.main --skip-processing

# Enable geocoding (requires API key)
python -m src.main --geocode

# Upload to S3 (requires AWS credentials)
python -m src.main --upload-s3
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
4. **Data Export**: Supports CSV, JSON, and Parquet formats with S3 upload
5. **Japanese Text**: Automatic normalization (full-width to half-width conversion)
6. **Data Processing**: Default enabled - normalizes data and performs quality checks
7. **Geocoding**: Optional feature using Google Maps API or free Nominatim

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

1. **Complete Scrapers**: Replace placeholder selectors with actual HTML structure for SUUMO and HOMES
2. **Enhanced Geocoding**: Add batch geocoding optimization
3. **Database Integration**: Add direct database storage option
4. **API Development**: Create REST API for accessing scraped data
5. **Async Scraping**: Implement asyncio for parallel scraping
6. **Testing**: Expand test coverage for all modules