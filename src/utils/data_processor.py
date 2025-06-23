"""
Data processing utilities for normalizing and cleaning scraped real estate data.
"""

import re
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from loguru import logger


class DataProcessor:
    """Handle data normalization and cleaning."""
    
    def __init__(self):
        # Floor plan normalization mappings
        self.floor_plan_mappings = {
            # Full-width to half-width conversion and variations
            '１Ｒ': '1R', '１Ｋ': '1K', '１ＤＫ': '1DK', '１ＬＤＫ': '1LDK',
            '２Ｋ': '2K', '２ＤＫ': '2DK', '２ＬＤＫ': '2LDK', '２ＬＤＫ＋Ｓ': '2LDK',
            '３ＤＫ': '3DK', '３ＬＤＫ': '3LDK', '４ＬＤＫ': '4LDK',
            # With service room variations
            '1LDK+S': '1LDK', '2LDK+S': '2LDK', '3LDK+S': '3LDK',
            '1SLDK': '1LDK', '2SLDK': '2LDK', '3SLDK': '3LDK',
        }
        
    def normalize_floor_plan(self, floor_plan: str) -> str:
        """
        Normalize floor plan notation.
        
        Examples:
            １ＬＤＫ -> 1LDK
            1LDK+S -> 1LDK
            2SLDK -> 2LDK
        """
        if not floor_plan:
            return ""
            
        # Convert to uppercase
        floor_plan = floor_plan.upper().strip()
        
        # Apply direct mappings
        if floor_plan in self.floor_plan_mappings:
            return self.floor_plan_mappings[floor_plan]
            
        # Convert full-width numbers to half-width
        floor_plan = floor_plan.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
        
        # Remove service room indicators
        floor_plan = re.sub(r'\+S$|S(?=[LDK])', '', floor_plan)
        
        # Standardize format (remove spaces, normalize order)
        floor_plan = re.sub(r'\s+', '', floor_plan)
        
        return floor_plan
    
    def normalize_rent(self, rent_str: str) -> Optional[int]:
        """
        Normalize rent string to integer value.
        
        Examples:
            12.5万円 -> 125000
            125,000円 -> 125000
            ¥125,000 -> 125000
        """
        if not rent_str or rent_str == '-':
            return None
            
        try:
            # Remove currency symbols and whitespace
            rent_str = rent_str.replace('¥', '').replace('円', '').replace(',', '')
            rent_str = rent_str.strip()
            
            # Handle 万円 format
            if '万' in rent_str:
                # Extract number before 万
                match = re.search(r'([\d.]+)万', rent_str)
                if match:
                    value = float(match.group(1))
                    return int(value * 10000)
                    
            # Direct numeric conversion
            rent_str = re.sub(r'[^\d.]', '', rent_str)
            if rent_str:
                return int(float(rent_str))
                
        except (ValueError, AttributeError) as e:
            logger.warning(f"Failed to normalize rent: {rent_str} - {e}")
            
        return None
    
    def normalize_area(self, area_str: str) -> Optional[float]:
        """
        Normalize area string to float value.
        
        Examples:
            35.00㎡ -> 35.0
            35m2 -> 35.0
            35平米 -> 35.0
        """
        if not area_str or area_str == '-':
            return None
            
        try:
            # Remove units and whitespace
            area_str = area_str.replace('㎡', '').replace('m2', '').replace('m²', '')
            area_str = area_str.replace('平米', '').replace('平方メートル', '')
            area_str = area_str.strip()
            
            # Extract numeric value
            match = re.search(r'[\d.]+', area_str)
            if match:
                return float(match.group())
                
        except (ValueError, AttributeError) as e:
            logger.warning(f"Failed to normalize area: {area_str} - {e}")
            
        return None
    
    def normalize_station_distance(self, distance_str: str) -> Optional[int]:
        """
        Normalize station distance to minutes.
        
        Examples:
            徒歩5分 -> 5
            駅徒歩5分 -> 5
            5分 -> 5
            バス10分 -> 10 (with note that it's bus)
        """
        if not distance_str or distance_str == '-':
            return None
            
        try:
            # Extract minutes
            match = re.search(r'(\d+)分', distance_str)
            if match:
                return int(match.group(1))
                
            # Try direct numeric conversion
            numeric_str = re.sub(r'[^\d]', '', distance_str)
            if numeric_str:
                return int(numeric_str)
                
        except (ValueError, AttributeError) as e:
            logger.warning(f"Failed to normalize station distance: {distance_str} - {e}")
            
        return None
    
    def normalize_fees(self, fee_str: str) -> Optional[int]:
        """
        Normalize various fees (management fee, deposit, key money).
        
        Examples:
            1ヶ月 -> 1 (as multiplier, needs rent context)
            50,000円 -> 50000
            なし -> 0
            - -> 0
        """
        if not fee_str:
            return None
            
        # Handle "none" cases
        if fee_str in ['-', 'なし', 'ナシ', '無し', '無', '0', '０']:
            return 0
            
        # Handle month-based fees (return as multiplier)
        month_match = re.search(r'(\d+)ヶ月|(\d+)ヵ月|(\d+)か月', fee_str)
        if month_match:
            return int(next(g for g in month_match.groups() if g))
            
        # Handle direct amount
        return self.normalize_rent(fee_str)
    
    def process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process entire DataFrame with all normalizations.
        """
        # Create a copy to avoid modifying original
        df = df.copy()
        
        # Normalize floor plans
        if 'floor_plan' in df.columns:
            df['floor_plan'] = df['floor_plan'].apply(self.normalize_floor_plan)
            
        # Normalize rent
        if 'rent' in df.columns and df['rent'].dtype == 'object':
            df['rent'] = df['rent'].apply(self.normalize_rent)
            
        # Normalize area
        if 'area' in df.columns and df['area'].dtype == 'object':
            df['area'] = df['area'].apply(self.normalize_area)
            
        # Normalize station distance
        if 'station_distance' in df.columns and df['station_distance'].dtype == 'object':
            df['station_distance'] = df['station_distance'].apply(self.normalize_station_distance)
            
        # Normalize fees
        for fee_col in ['management_fee', 'deposit', 'key_money']:
            if fee_col in df.columns and df[fee_col].dtype == 'object':
                df[fee_col] = df[fee_col].apply(self.normalize_fees)
                
        logger.info(f"Processed {len(df)} properties")
        return df
    
    def standardize_column_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column data types for consistency.
        """
        type_mappings = {
            'rent': 'int64',
            'management_fee': 'Int64',  # Nullable integer
            'deposit': 'Int64',
            'key_money': 'Int64',
            'area': 'float64',
            'floor_number': 'Int64',
            'total_floors': 'Int64',
            'building_age': 'Int64',
            'construction_year': 'Int64',
            'station_distance': 'Int64',
            'latitude': 'float64',
            'longitude': 'float64'
        }
        
        for col, dtype in type_mappings.items():
            if col in df.columns:
                try:
                    if dtype == 'Int64':  # Nullable integer
                        df[col] = pd.array(df[col], dtype="Int64")
                    else:
                        df[col] = df[col].astype(dtype, errors='ignore')
                except Exception as e:
                    logger.warning(f"Failed to convert {col} to {dtype}: {e}")
                    
        return df