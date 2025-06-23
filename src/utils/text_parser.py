"""
Japanese text parsing and normalization utilities.
"""

import re
from typing import Optional, Tuple
import unicodedata
from loguru import logger


class JapaneseTextParser:
    """Parser for normalizing Japanese property text data."""
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize Japanese text (全角 to 半角 for numbers and English)."""
        if not text:
            return ""
            
        # Convert full-width numbers and English to half-width
        text = unicodedata.normalize('NFKC', text)
        
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @staticmethod
    def parse_rent(rent_text: str) -> Optional[int]:
        """
        Parse rent amount from text.
        Examples: "8.5万円" -> 85000, "10万円" -> 100000
        """
        if not rent_text:
            return None
            
        try:
            # Normalize text
            rent_text = JapaneseTextParser.normalize_text(rent_text)
            
            # Remove currency symbols and spaces
            rent_text = rent_text.replace('円', '').replace('¥', '').replace(',', '').strip()
            
            # Handle 万 (10,000) unit
            if '万' in rent_text:
                # Extract number before 万
                match = re.search(r'([\d.]+)\s*万', rent_text)
                if match:
                    value = float(match.group(1))
                    return int(value * 10000)
            
            # Try to extract any number
            match = re.search(r'[\d,]+', rent_text)
            if match:
                return int(match.group().replace(',', ''))
                
        except Exception as e:
            logger.error(f"Failed to parse rent '{rent_text}': {str(e)}")
            
        return None
    
    @staticmethod
    def parse_area(area_text: str) -> Optional[float]:
        """
        Parse area in square meters.
        Examples: "25.5㎡" -> 25.5, "30m²" -> 30.0
        """
        if not area_text:
            return None
            
        try:
            # Normalize text
            area_text = JapaneseTextParser.normalize_text(area_text)
            
            # Remove area units
            area_text = re.sub(r'[㎡m²平米]', '', area_text).strip()
            
            # Extract number
            match = re.search(r'[\d.]+', area_text)
            if match:
                return float(match.group())
                
        except Exception as e:
            logger.error(f"Failed to parse area '{area_text}': {str(e)}")
            
        return None
    
    @staticmethod
    def parse_floor_plan(layout_text: str) -> str:
        """
        Normalize floor plan text.
        Examples: "１ＬＤＫ" -> "1LDK", "2DK" -> "2DK"
        """
        if not layout_text:
            return ""
            
        # Normalize text
        layout_text = JapaneseTextParser.normalize_text(layout_text)
        
        # Common patterns
        layout_text = layout_text.upper()
        layout_text = re.sub(r'\s+', '', layout_text)
        
        return layout_text
    
    @staticmethod
    def parse_station_distance(distance_text: str) -> Optional[int]:
        """
        Parse walking distance to station in minutes.
        Examples: "徒歩5分" -> 5, "歩10分" -> 10
        """
        if not distance_text:
            return None
            
        try:
            # Normalize text
            distance_text = JapaneseTextParser.normalize_text(distance_text)
            
            # Extract minutes
            match = re.search(r'(\d+)\s*分', distance_text)
            if match:
                return int(match.group(1))
                
        except Exception as e:
            logger.error(f"Failed to parse station distance '{distance_text}': {str(e)}")
            
        return None
    
    @staticmethod
    def parse_building_age(age_text: str) -> Optional[int]:
        """
        Parse building age in years.
        Examples: "築5年" -> 5, "築年数: 10年" -> 10
        """
        if not age_text:
            return None
            
        try:
            # Normalize text
            age_text = JapaneseTextParser.normalize_text(age_text)
            
            # Extract years after 築
            match = re.search(r'築\s*(\d+)\s*年', age_text)
            if match:
                return int(match.group(1))
            
            # Alternative pattern
            match = re.search(r'(\d+)\s*年', age_text)
            if match and '築' in age_text:
                return int(match.group(1))
                
        except Exception as e:
            logger.error(f"Failed to parse building age '{age_text}': {str(e)}")
            
        return None
    
    @staticmethod
    def parse_floor_info(floor_text: str) -> Tuple[Optional[int], Optional[int]]:
        """
        Parse floor number and total floors.
        Examples: "3階/5階建" -> (3, 5), "2F" -> (2, None)
        Returns: (floor_number, total_floors)
        """
        if not floor_text:
            return None, None
            
        try:
            # Normalize text
            floor_text = JapaneseTextParser.normalize_text(floor_text)
            
            # Pattern: X階/Y階建
            match = re.search(r'(\d+)\s*階?\s*/\s*(\d+)\s*階?', floor_text)
            if match:
                return int(match.group(1)), int(match.group(2))
            
            # Pattern: X階 or XF
            match = re.search(r'(\d+)\s*[階F]', floor_text)
            if match:
                return int(match.group(1)), None
                
        except Exception as e:
            logger.error(f"Failed to parse floor info '{floor_text}': {str(e)}")
            
        return None, None
    
    @staticmethod
    def extract_address_components(address: str) -> dict:
        """
        Extract components from Japanese address.
        Returns dict with prefecture, city, district, etc.
        """
        components = {
            'prefecture': '',
            'city': '',
            'district': '',
            'detail': ''
        }
        
        if not address:
            return components
            
        # Normalize
        address = JapaneseTextParser.normalize_text(address)
        
        # Extract prefecture
        prefecture_match = re.match(r'(東京都|.+?[都道府県])', address)
        if prefecture_match:
            components['prefecture'] = prefecture_match.group(1)
            address = address[len(components['prefecture']):]
        
        # Extract city/ward
        city_match = re.match(r'(.+?[市区町村])', address)
        if city_match:
            components['city'] = city_match.group(1)
            address = address[len(components['city']):]
        
        # Remaining is district/detail
        if address:
            parts = address.split(' ', 1)
            components['district'] = parts[0]
            if len(parts) > 1:
                components['detail'] = parts[1]
        
        return components