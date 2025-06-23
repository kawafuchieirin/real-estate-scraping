"""
Data export utilities for saving scraped data.
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import pandas as pd
from loguru import logger

from ..models.property import Property
from ..config.settings import settings


class DataExporter:
    """Handle data export to various formats."""
    
    def __init__(self):
        self.raw_dir = Path(settings.RAW_DATA_DIR)
        self.processed_dir = Path(settings.PROCESSED_DATA_DIR)
        
        # Create directories if they don't exist
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
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