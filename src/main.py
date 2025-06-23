"""
Main script for real estate scraping.
"""

import argparse
from typing import List
from loguru import logger

from .config.settings import settings
from .scrapers.suumo import SuumoScraper
from .scrapers.homes import HomesScraper
from .models.property import Property
from .utils.data_export import DataExporter
from .utils.logger import setup_logger


def main(
    sites: List[str] = None,
    areas: List[str] = None,
    property_types: List[str] = None,
    max_pages: int = 5,
    export_format: str = 'csv'
):
    """
    Main function to orchestrate the scraping process.
    
    Args:
        sites: List of site names to scrape
        areas: List of area codes to scrape
        property_types: List of property type codes
        max_pages: Maximum number of pages to scrape per search
        export_format: Export format (csv, json, parquet)
    """
    logger.info("Starting real estate scraping")
    
    # Default to all if not specified
    if not sites:
        sites = [site['name'] for site in settings.TARGET_SITES]
    if not areas:
        areas = [area['code'] for area in settings.TARGET_AREAS[:3]]  # Start with first 3 areas
    if not property_types:
        property_types = [pt['code'] for pt in settings.PROPERTY_TYPES]
    
    # Initialize scrapers
    scrapers = {
        'SUUMO': SuumoScraper(),
        'HOMES': HomesScraper(),
    }
    
    all_properties = []
    
    # Iterate through sites
    for site_name in sites:
        if site_name not in scrapers:
            logger.warning(f"Scraper for {site_name} not implemented yet")
            continue
            
        scraper = scrapers[site_name]
        
        # Check robots.txt
        site_config = next((s for s in settings.TARGET_SITES if s['name'] == site_name), None)
        if site_config and not scraper.check_robots_txt(site_config['robots_txt']):
            logger.warning(f"Skipping {site_name} due to robots.txt restrictions")
            continue
        
        # Iterate through areas and property types
        for area_code in areas:
            area = next((a for a in settings.TARGET_AREAS if a['code'] == area_code), None)
            if not area:
                continue
                
            for prop_type_code in property_types:
                prop_type = next((pt for pt in settings.PROPERTY_TYPES if pt['code'] == prop_type_code), None)
                if not prop_type:
                    continue
                    
                logger.info(f"Scraping {site_name} - {area['name']} - {prop_type['name']}")
                
                try:
                    properties = scraper.scrape_area(area, prop_type, max_pages)
                    all_properties.extend(properties)
                except Exception as e:
                    logger.error(f"Error scraping {site_name} - {area['name']}: {str(e)}")
                    continue
    
    # Export data
    if all_properties:
        exporter = DataExporter()
        
        if export_format == 'csv':
            filepath = exporter.export_to_csv(all_properties)
        elif export_format == 'json':
            filepath = exporter.export_to_json(all_properties)
        elif export_format == 'parquet':
            filepath = exporter.export_to_parquet(all_properties)
        else:
            logger.error(f"Unknown export format: {export_format}")
            return
            
        # Create summary report
        summary = exporter.create_summary_report(all_properties)
        logger.info(f"Scraping completed. Total properties: {summary['total_properties']}")
    else:
        logger.warning("No properties were scraped")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Real Estate Scraper")
    parser.add_argument(
        "--sites",
        nargs="+",
        help="Sites to scrape (e.g., SUUMO HOMES)"
    )
    parser.add_argument(
        "--areas",
        nargs="+",
        help="Area codes to scrape (e.g., 13101 13102)"
    )
    parser.add_argument(
        "--property-types",
        nargs="+",
        help="Property type codes (e.g., apartment house)"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=5,
        help="Maximum pages to scrape per search"
    )
    parser.add_argument(
        "--export-format",
        choices=['csv', 'json', 'parquet'],
        default='csv',
        help="Export format for scraped data"
    )
    
    args = parser.parse_args()
    
    main(
        sites=args.sites,
        areas=args.areas,
        property_types=args.property_types,
        max_pages=args.max_pages,
        export_format=args.export_format
    )