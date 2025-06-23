#!/usr/bin/env python3
"""
Example script demonstrating data processing, normalization, geocoding, and S3 upload.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.property import Property
from src.utils import DataExporter, DataProcessor, Geocoder, DataQualityChecker
from src.utils.logger import setup_logger

# Load environment variables
load_dotenv()

# Setup logger
logger = setup_logger()


def create_sample_properties():
    """Create sample property data for demonstration."""
    return [
        Property(
            property_id="suumo_001",
            site_name="SUUMO",
            url="https://suumo.jp/chintai/jnc_000012345678/",
            title="東京都渋谷区の1LDKマンション",
            property_type="マンション",
            prefecture="東京都",
            city="渋谷区",
            district="恵比寿",
            address="東京都渋谷区恵比寿1-2-3",
            rent=125000,
            management_fee=5000,
            deposit=125000,
            key_money=125000,
            floor_plan="１ＬＤＫ",  # Full-width characters
            area=35.5,
            floor_number=3,
            total_floors=10,
            building_age=5,
            construction_year=2019,
            nearest_station="恵比寿駅",
            station_distance=5,
            train_lines=["JR山手線", "東京メトロ日比谷線"],
            features=["オートロック", "宅配ボックス", "エアコン"]
        ),
        Property(
            property_id="suumo_002",
            site_name="SUUMO",
            url="https://suumo.jp/chintai/jnc_000012345679/",
            title="港区六本木の高級マンション",
            property_type="マンション",
            prefecture="東京都",
            city="港区",
            district="六本木",
            address="東京都港区六本木4-5-6",
            rent=350000,  # High-end property
            management_fee=15000,
            deposit=700000,
            key_money=350000,
            floor_plan="2LDK+S",  # With service room
            area=75.0,
            floor_number=25,
            total_floors=30,
            building_age=2,
            construction_year=2022,
            nearest_station="六本木駅",
            station_distance=3,
            train_lines=["東京メトロ日比谷線", "都営大江戸線"],
            features=["コンシェルジュ", "ジム", "展望ラウンジ"]
        ),
        Property(
            property_id="suumo_003",
            site_name="SUUMO",
            url="https://suumo.jp/chintai/jnc_000012345680/",
            title="世田谷区のファミリー向けマンション",
            property_type="マンション",
            prefecture="東京都",
            city="世田谷区",
            district="三軒茶屋",
            address="東京都世田谷区三軒茶屋2-10-5",
            rent=180000,
            management_fee=8000,
            deposit=180000,
            key_money=0,  # No key money
            floor_plan="３ＬＤＫ",
            area=65.5,
            floor_number=5,
            total_floors=8,
            building_age=10,
            construction_year=2014,
            nearest_station="三軒茶屋駅",
            station_distance=8,
            train_lines=["東急田園都市線", "東急世田谷線"],
            features=["ペット可", "駐車場", "専用庭"]
        )
    ]


def demonstrate_data_processing():
    """Demonstrate the complete data processing pipeline."""
    
    logger.info("Starting data processing demonstration...")
    
    # Create sample properties
    properties = create_sample_properties()
    logger.info(f"Created {len(properties)} sample properties")
    
    # Initialize data exporter with processors
    exporter = DataExporter()
    
    # Process and export data with all features
    logger.info("\n=== Processing data with normalization, geocoding, and quality checks ===")
    
    # Note: Set apply_geocoding=False if you don't have API keys configured
    # Set upload_to_s3=False if you don't have AWS credentials configured
    result = exporter.process_and_export(
        properties,
        export_format="csv",
        apply_geocoding=False,  # Set to True if you have geocoding API configured
        upload_to_s3=False      # Set to True if you have AWS S3 configured
    )
    
    # Display results
    logger.info("\n=== Processing Results ===")
    logger.info(f"Records processed: {result['records_processed']}")
    logger.info(f"Quality score: {result['quality_score']}/100")
    logger.info(f"Local file saved: {result['local_path']}")
    
    if result['s3_path']:
        logger.info(f"S3 upload successful: {result['s3_path']}")
    else:
        logger.info("S3 upload skipped (no credentials or disabled)")
        
    # Display quality report summary
    quality_report = result['quality_report']
    logger.info("\n=== Quality Report Summary ===")
    logger.info(f"Total records: {quality_report['total_records']}")
    
    if quality_report['missing_values']:
        logger.info("\nMissing values:")
        for col, info in quality_report['missing_values'].items():
            logger.info(f"  - {col}: {info['count']} ({info['percentage']}%)")
            
    if quality_report['outliers']:
        logger.info("\nOutliers detected:")
        for col, outliers in quality_report['outliers'].items():
            logger.info(f"  - {col}: {len(outliers)} outliers")
            
    # Demonstrate individual components
    demonstrate_normalization()
    demonstrate_geocoding()
    demonstrate_quality_checks()
    

def demonstrate_normalization():
    """Demonstrate data normalization features."""
    logger.info("\n=== Data Normalization Examples ===")
    
    processor = DataProcessor()
    
    # Floor plan normalization
    floor_plans = ["１ＬＤＫ", "1LDK+S", "2SLDK", "３ＤＫ"]
    logger.info("\nFloor plan normalization:")
    for fp in floor_plans:
        normalized = processor.normalize_floor_plan(fp)
        logger.info(f"  {fp} → {normalized}")
        
    # Rent normalization
    rents = ["12.5万円", "125,000円", "¥125,000", "250000"]
    logger.info("\nRent normalization:")
    for rent in rents:
        normalized = processor.normalize_rent(rent)
        logger.info(f"  {rent} → {normalized}")
        
    # Area normalization
    areas = ["35.00㎡", "35m2", "35平米", "45.5"]
    logger.info("\nArea normalization:")
    for area in areas:
        normalized = processor.normalize_area(area)
        logger.info(f"  {area} → {normalized}")
        
    # Station distance normalization
    distances = ["徒歩5分", "駅徒歩10分", "15分", "バス20分"]
    logger.info("\nStation distance normalization:")
    for dist in distances:
        normalized = processor.normalize_station_distance(dist)
        logger.info(f"  {dist} → {normalized}")


def demonstrate_geocoding():
    """Demonstrate geocoding functionality."""
    logger.info("\n=== Geocoding Examples ===")
    
    # Note: This requires either Google Maps API key or uses free Nominatim service
    geocoder = Geocoder(provider="nominatim")  # Use "google" if you have API key
    
    addresses = [
        "東京都渋谷区恵比寿1-2-3",
        "東京都港区六本木4-5-6",
        "東京都世田谷区三軒茶屋2-10-5"
    ]
    
    logger.info("\nGeocoding addresses (using Nominatim):")
    for address in addresses:
        coords = geocoder.geocode(address)
        if coords:
            logger.info(f"  {address} → ({coords[0]}, {coords[1]})")
        else:
            logger.info(f"  {address} → Failed to geocode")


def demonstrate_quality_checks():
    """Demonstrate data quality checking."""
    logger.info("\n=== Data Quality Checks ===")
    
    import pandas as pd
    
    # Create sample data with some quality issues
    data = {
        'property_id': ['001', '002', '003', '003'],  # Duplicate
        'site_name': ['SUUMO', 'SUUMO', 'HOMES', 'HOMES'],
        'url': ['url1', 'url2', 'url3', 'url3'],  # Duplicate
        'city': ['渋谷区', '港区', '世田谷区', '世田谷区'],
        'rent': [125000, 350000, -1000, 10000000],  # Outliers
        'area': [35.5, 75.0, 0, 1000],  # Outliers
        'floor_plan': ['1LDK', '2LDK', None, '3LDK'],  # Missing value
        'latitude': [35.6, 35.7, 100.0, 35.8],  # Invalid coordinate
        'longitude': [139.7, 139.8, 200.0, 139.9]  # Invalid coordinate
    }
    
    df = pd.DataFrame(data)
    
    checker = DataQualityChecker()
    report = checker.check_data_quality(df)
    
    logger.info(f"\nQuality Score: {report['quality_score']}/100")
    logger.info(f"Duplicates found: {len(report['duplicates'])} types")
    logger.info(f"Outliers found: {len(report['outliers'])} columns")
    
    # Apply fixes
    logger.info("\nApplying automatic fixes...")
    fixed_df = checker.fix_common_issues(df)
    logger.info(f"Records after fixes: {len(fixed_df)} (was {len(df)})")


if __name__ == "__main__":
    demonstrate_data_processing()