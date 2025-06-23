#!/usr/bin/env python3
"""
Example script demonstrating how to use the real estate scraper.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.main import main
from src.config.settings import settings
from loguru import logger


def example_basic_scraping():
    """Basic scraping example - scrape first 3 areas."""
    logger.info("=== Basic Scraping Example ===")
    
    # Scrape with default settings (first 3 areas, all property types)
    # Data processing is enabled by default
    main(
        sites=['SUUMO'],
        max_pages=2,
        export_format='csv',
        process_data=True  # Default behavior
    )


def example_specific_area():
    """Scrape specific areas and property types."""
    logger.info("=== Specific Area Example ===")
    
    # Scrape Shibuya and Shinjuku apartments only
    main(
        sites=['SUUMO', 'HOMES'],
        areas=['13113', '13104'],  # Shibuya, Shinjuku
        property_types=['apartment'],  # Mansion only
        max_pages=3,
        export_format='json'
    )


def example_all_areas():
    """Scrape all Tokyo 23 wards (use with caution!)."""
    logger.info("=== All Areas Example (Limited) ===")
    
    # Get all area codes
    all_areas = [area['code'] for area in settings.TARGET_AREAS]
    
    # Scrape all areas but limit to 1 page per search
    main(
        sites=['SUUMO'],
        areas=all_areas[:5],  # Limit to first 5 for example
        property_types=['apartment', 'apart'],
        max_pages=1,
        export_format='parquet'
    )


def example_custom_export():
    """Example with multiple export formats."""
    logger.info("=== Custom Export Example ===")
    
    # First scrape and export as CSV
    main(
        sites=['HOMES'],
        areas=['13110'],  # Meguro
        property_types=['apartment'],
        max_pages=2,
        export_format='csv'
    )
    
    # Same data but export as JSON
    main(
        sites=['HOMES'],
        areas=['13110'],  # Meguro
        property_types=['apartment'],
        max_pages=2,
        export_format='json'
    )


def show_available_options():
    """Display available options for scraping."""
    print("\n=== Available Options ===")
    
    print("\nTarget Sites:")
    for site in settings.TARGET_SITES:
        print(f"  - {site['name']}: {site['base_url']}")
    
    print("\nTokyo 23 Wards:")
    for i, area in enumerate(settings.TARGET_AREAS):
        print(f"  {area['code']}: {area['name']}", end="")
        if (i + 1) % 4 == 0:
            print()  # New line every 4 items
    print()
    
    print("\nProperty Types:")
    for prop_type in settings.PROPERTY_TYPES:
        print(f"  - {prop_type['code']}: {prop_type['name']}")
    
    print("\nExport Formats:")
    print("  - csv: Comma-separated values (Excel compatible)")
    print("  - json: JavaScript Object Notation")
    print("  - parquet: Apache Parquet (for big data processing)")


def example_with_processing():
    """Example with data processing and geocoding."""
    logger.info("=== Data Processing Example ===")
    
    # Scrape with data processing and geocoding enabled
    main(
        sites=['SUUMO'],
        areas=['13113'],  # Shibuya
        property_types=['apartment'],
        max_pages=1,
        export_format='csv',
        process_data=True,
        apply_geocoding=False,  # Set to True if you have API key
        upload_to_s3=False     # Set to True if you have AWS credentials
    )


def example_raw_data():
    """Example without data processing - raw data only."""
    logger.info("=== Raw Data Example ===")
    
    # Scrape without processing for raw data
    main(
        sites=['SUUMO'],
        areas=['13104'],  # Shinjuku
        property_types=['apart'],
        max_pages=1,
        export_format='json',
        process_data=False  # Skip normalization and quality checks
    )


if __name__ == "__main__":
    # Show available options
    show_available_options()
    
    # Run examples
    print("\n" + "="*50)
    
    # Uncomment the example you want to run:
    
    example_basic_scraping()
    # example_specific_area()
    # example_all_areas()
    # example_custom_export()
    # example_with_processing()
    # example_raw_data()
    
    print("\nScraping completed! Check the data/ directory for output files.")
    print("\nNote: To enable geocoding or S3 upload, set up the required API keys and credentials in .env file.")