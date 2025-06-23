"""
Data export utilities for saving scraped data.
"""

import json
import csv
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
import boto3
from botocore.exceptions import ClientError
from loguru import logger

from ..models.property import Property
from ..config.settings import settings
from .data_processor import DataProcessor
from .geocoding import Geocoder
from .data_quality import DataQualityChecker


class DataExporter:
    """Handle data export to various formats with S3 support."""
    
    def __init__(self):
        self.raw_dir = Path(settings.RAW_DATA_DIR)
        self.processed_dir = Path(settings.PROCESSED_DATA_DIR)
        
        # Create directories if they don't exist
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize processors
        self.data_processor = DataProcessor()
        self.geocoder = Geocoder()
        self.quality_checker = DataQualityChecker()
        
        # Initialize S3 client if credentials are available
        self.s3_client = None
        self.s3_bucket = os.getenv("S3_BUCKET_NAME", "real-estate-data")
        
        if os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"):
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                    region_name=os.getenv("AWS_REGION", "ap-northeast-1")
                )
                logger.info("S3 client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize S3 client: {e}")
                self.s3_client = None
    
    def export_to_json(self, properties: List[Property], filename: str = None) -> str:
        """Export properties to JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"properties_{timestamp}.json"
            
        filepath = self.raw_dir / filename
        
        data = [prop.model_dump() for prop in properties]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
        logger.info(f"Exported {len(properties)} properties to {filepath}")
        return str(filepath)
    
    def export_to_csv(self, properties: List[Property], filename: str = None) -> str:
        """Export properties to CSV file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"properties_{timestamp}.csv"
            
        filepath = self.processed_dir / filename
        
        # Convert to DataFrame for easier CSV export
        df = pd.DataFrame([prop.model_dump() for prop in properties])
        
        # Flatten nested fields
        if 'train_lines' in df.columns:
            df['train_lines'] = df['train_lines'].apply(
                lambda x: ', '.join(x) if isinstance(x, list) else ''
            )
        if 'features' in df.columns:
            df['features'] = df['features'].apply(
                lambda x: ', '.join(x) if isinstance(x, list) else ''
            )
            
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        logger.info(f"Exported {len(properties)} properties to {filepath}")
        return str(filepath)
    
    def export_to_parquet(self, properties: List[Property], filename: str = None) -> str:
        """Export properties to Parquet file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"properties_{timestamp}.parquet"
            
        filepath = self.processed_dir / filename
        
        # Convert to DataFrame
        df = pd.DataFrame([prop.model_dump() for prop in properties])
        
        # Convert datetime columns
        for col in ['scraped_at', 'updated_at']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])
                
        df.to_parquet(filepath, index=False, engine='pyarrow')
        
        logger.info(f"Exported {len(properties)} properties to {filepath}")
        return str(filepath)
    
    def create_summary_report(self, properties: List[Property]) -> Dict[str, Any]:
        """Create a summary report of scraped properties."""
        df = pd.DataFrame([prop.model_dump() for prop in properties])
        
        summary = {
            'total_properties': len(properties),
            'by_site': df['site_name'].value_counts().to_dict(),
            'by_city': df['city'].value_counts().to_dict(),
            'by_property_type': df['property_type'].value_counts().to_dict(),
            'by_floor_plan': df['floor_plan'].value_counts().to_dict(),
            'rent_statistics': {
                'mean': int(df['rent'].mean()),
                'median': int(df['rent'].median()),
                'min': int(df['rent'].min()),
                'max': int(df['rent'].max())
            },
            'area_statistics': {
                'mean': round(df['area'].mean(), 2),
                'median': round(df['area'].median(), 2),
                'min': round(df['area'].min(), 2),
                'max': round(df['area'].max(), 2)
            }
        }
        
        # Save summary
        summary_path = self.processed_dir / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Created summary report at {summary_path}")
        return summary
    
    def process_and_export(self, properties: List[Property], 
                          export_format: str = "csv",
                          apply_geocoding: bool = True,
                          upload_to_s3: bool = True) -> Dict[str, Any]:
        """
        Process properties with normalization, geocoding, and quality checks before export.
        
        Args:
            properties: List of Property objects
            export_format: Export format ('csv', 'json', 'parquet')
            apply_geocoding: Whether to geocode addresses
            upload_to_s3: Whether to upload to S3
            
        Returns:
            Dictionary with export results
        """
        # Convert to DataFrame
        df = pd.DataFrame([prop.model_dump() for prop in properties])
        
        # Apply data normalization
        logger.info("Applying data normalization...")
        df = self.data_processor.process_dataframe(df)
        df = self.data_processor.standardize_column_types(df)
        
        # Apply geocoding if requested
        if apply_geocoding and 'address' in df.columns:
            logger.info("Geocoding addresses...")
            addresses_to_geocode = df[df['latitude'].isna() & df['address'].notna()]['address'].unique()
            
            if len(addresses_to_geocode) > 0:
                geocoding_results = self.geocoder.batch_geocode(list(addresses_to_geocode))
                
                # Apply geocoding results
                for address, coords in geocoding_results.items():
                    if coords:
                        mask = (df['address'] == address) & df['latitude'].isna()
                        df.loc[mask, 'latitude'] = coords[0]
                        df.loc[mask, 'longitude'] = coords[1]
                        
        # Run quality checks
        logger.info("Running data quality checks...")
        quality_report = self.quality_checker.check_data_quality(df)
        
        # Fix common issues
        df = self.quality_checker.fix_common_issues(df)
        
        # Generate filename with date
        now = datetime.now()
        date_str = now.strftime("%Y/%m/%d")
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        city = df['city'].mode()[0] if 'city' in df.columns and not df['city'].empty else 'tokyo'
        
        # Export to specified format
        if export_format == "csv":
            filename = f"{timestamp}_{city}.csv"
            local_path = self._export_df_to_csv(df, filename)
        elif export_format == "json":
            filename = f"{timestamp}_{city}.json"
            local_path = self._export_df_to_json(df, filename)
        elif export_format == "parquet":
            filename = f"{timestamp}_{city}.parquet"
            local_path = self._export_df_to_parquet(df, filename)
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
            
        # Upload to S3 if requested
        s3_path = None
        if upload_to_s3 and self.s3_client:
            s3_key = f"raw/{city}/{date_str}_{city}.{export_format}"
            s3_path = self.upload_to_s3(local_path, s3_key)
            
        # Save quality report
        quality_report_path = self.processed_dir / f"quality_report_{timestamp}.json"
        with open(quality_report_path, 'w', encoding='utf-8') as f:
            json.dump(quality_report, f, ensure_ascii=False, indent=2)
            
        return {
            'local_path': local_path,
            's3_path': s3_path,
            'quality_report': quality_report,
            'quality_report_path': str(quality_report_path),
            'records_processed': len(df),
            'quality_score': quality_report['quality_score']
        }
    
    def _export_df_to_csv(self, df: pd.DataFrame, filename: str) -> str:
        """Export DataFrame to CSV file."""
        filepath = self.processed_dir / filename
        
        # Flatten nested fields
        if 'train_lines' in df.columns:
            df['train_lines'] = df['train_lines'].apply(
                lambda x: ', '.join(x) if isinstance(x, list) else ''
            )
        if 'features' in df.columns:
            df['features'] = df['features'].apply(
                lambda x: ', '.join(x) if isinstance(x, list) else ''
            )
            
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        logger.info(f"Exported {len(df)} properties to {filepath}")
        return str(filepath)
    
    def _export_df_to_json(self, df: pd.DataFrame, filename: str) -> str:
        """Export DataFrame to JSON file."""
        filepath = self.processed_dir / filename
        
        # Convert to records format
        data = df.to_dict('records')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
        logger.info(f"Exported {len(df)} properties to {filepath}")
        return str(filepath)
    
    def _export_df_to_parquet(self, df: pd.DataFrame, filename: str) -> str:
        """Export DataFrame to Parquet file."""
        filepath = self.processed_dir / filename
        
        # Convert datetime columns
        for col in ['scraped_at', 'updated_at']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])
                
        df.to_parquet(filepath, index=False, engine='pyarrow')
        logger.info(f"Exported {len(df)} properties to {filepath}")
        return str(filepath)
    
    def upload_to_s3(self, local_path: str, s3_key: str) -> Optional[str]:
        """
        Upload file to S3.
        
        Args:
            local_path: Local file path
            s3_key: S3 key (path) for the file
            
        Returns:
            S3 URI if successful, None otherwise
        """
        if not self.s3_client:
            logger.warning("S3 client not initialized, skipping upload")
            return None
            
        try:
            self.s3_client.upload_file(local_path, self.s3_bucket, s3_key)
            s3_uri = f"s3://{self.s3_bucket}/{s3_key}"
            logger.info(f"Uploaded file to {s3_uri}")
            return s3_uri
        except ClientError as e:
            logger.error(f"Failed to upload to S3: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during S3 upload: {e}")
            return None