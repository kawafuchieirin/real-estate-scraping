"""
HOMES real estate website scraper.
"""

import re
from typing import List, Dict, Optional, Any
from datetime import datetime
from bs4 import BeautifulSoup
from loguru import logger

from .base import BaseScraper
from ..models.property import Property, PropertySearchResult
from ..utils.text_parser import JapaneseTextParser


class HomesScraper(BaseScraper):
    """Scraper for HOMES real estate website."""
    
    def __init__(self):
        super().__init__(
            site_name="HOMES",
            base_url="https://www.homes.co.jp"
        )
        self.parser = JapaneseTextParser()
        
    def search_properties(
        self,
        area: Dict[str, str],
        property_type: Dict[str, str],
        page: int = 1
    ) -> Optional[PropertySearchResult]:
        """Search for properties on HOMES."""
        # Note: This is a placeholder implementation
        # Actual URLs and parsing logic would need to be implemented based on HOMES's structure
        
        # Map property types to HOMES format
        type_mapping = {
            'apartment': 'mansion',
            'apart': 'apart',
            'house': 'kodate'
        }
        
        property_type_code = type_mapping.get(property_type['code'], 'mansion')
        
        # Construct search URL (this is an example - actual URL structure may differ)
        search_url = f"{self.base_url}/chintai/{property_type_code}/tokyo/{area['code']}/"
        if page > 1:
            search_url += f"?page={page}"
            
        response = self._make_request(search_url)
        if not response:
            return None
            
        soup = self._parse_html(response.text)
        property_list = self.parse_property_list(soup)
        
        properties = []
        for prop_data in property_list:
            property_obj = self.parse_property_details(prop_data)
            if property_obj:
                properties.append(property_obj)
                
        return PropertySearchResult(
            site_name=self.site_name,
            search_area=area['name'],
            property_type=property_type['name'],
            total_count=len(properties),
            page_number=page,
            properties=properties
        )
    
    def parse_property_list(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse property list from HOMES search results."""
        properties = []
        
        # This is a placeholder - actual selectors would need to be determined
        # by inspecting HOMES's HTML structure
        property_items = soup.find_all('div', class_='mod-mergeBuilding')
        
        for item in property_items:
            try:
                # Extract basic information from list view
                prop_data = {
                    'url': self._extract_url(item),
                    'title': self._extract_title(item),
                    'rent': self._extract_rent(item),
                    'floor_plan': self._extract_floor_plan(item),
                    'area': self._extract_area(item),
                    'address': self._extract_address(item),
                    'building_age': self._extract_building_age(item),
                    'floor_info': self._extract_floor_info(item),
                    'station_info': self._extract_station_info(item)
                }
                properties.append(prop_data)
            except Exception as e:
                logger.error(f"Error parsing property item: {str(e)}")
                continue
                
        return properties
    
    def parse_property_details(self, property_data: Dict[str, Any]) -> Optional[Property]:
        """Parse individual property details."""
        try:
            # Generate a unique ID
            property_id = f"homes_{hash(property_data.get('url', ''))}"
            
            # Parse rent
            rent = self.parser.parse_rent(property_data.get('rent', ''))
            
            # Parse area
            area = self.parser.parse_area(property_data.get('area', ''))
            
            # Parse floor plan
            floor_plan = self.parser.parse_floor_plan(property_data.get('floor_plan', ''))
            
            # Parse station distance
            station_distance = None
            if property_data.get('station_info'):
                station_distance = self.parser.parse_station_distance(
                    property_data['station_info'].get('distance', '')
                )
            
            # Parse building age
            building_age = self.parser.parse_building_age(property_data.get('building_age', ''))
            
            # Parse floor info
            floor_number, total_floors = self.parser.parse_floor_info(
                property_data.get('floor_info', '')
            )
            
            # Extract address components
            address_components = self.parser.extract_address_components(
                property_data.get('address', '')
            )
            
            return Property(
                property_id=property_id,
                site_name=self.site_name,
                url=property_data.get('url', ''),
                title=property_data.get('title', ''),
                property_type=property_data.get('property_type', 'マンション'),
                prefecture=address_components.get('prefecture', '東京都'),
                city=address_components.get('city', ''),
                district=address_components.get('district'),
                address=property_data.get('address', ''),
                rent=rent or 0,
                floor_plan=floor_plan,
                area=area or 0.0,
                floor_number=floor_number,
                total_floors=total_floors,
                building_age=building_age,
                nearest_station=property_data.get('station_info', {}).get('name'),
                station_distance=station_distance
            )
        except Exception as e:
            logger.error(f"Error creating property object: {str(e)}")
            return None
    
    def _extract_url(self, item: BeautifulSoup) -> str:
        """Extract property URL."""
        link = item.find('a', class_='bukkenName')
        if link and link.get('href'):
            return self.base_url + link['href']
        return ''
    
    def _extract_title(self, item: BeautifulSoup) -> str:
        """Extract property title."""
        title_elem = item.find('h2', class_='bukkenName')
        return title_elem.text.strip() if title_elem else ''
    
    def _extract_rent(self, item: BeautifulSoup) -> str:
        """Extract rent amount."""
        rent_elem = item.find('span', class_='priceLabel')
        return rent_elem.text.strip() if rent_elem else '0'
    
    def _extract_floor_plan(self, item: BeautifulSoup) -> str:
        """Extract floor plan."""
        plan_elem = item.find('span', class_='layout')
        return plan_elem.text.strip() if plan_elem else ''
    
    def _extract_area(self, item: BeautifulSoup) -> str:
        """Extract property area."""
        area_elem = item.find('span', class_='space')
        return area_elem.text.strip() if area_elem else '0'
    
    def _extract_address(self, item: BeautifulSoup) -> str:
        """Extract address."""
        addr_elem = item.find('div', class_='bukkenSpec')
        if addr_elem:
            # Extract from specific pattern
            text = addr_elem.text
            match = re.search(r'(東京都.+?[区市].*?)(?:\s|$)', text)
            if match:
                return match.group(1).strip()
        return ''
    
    def _extract_building_age(self, item: BeautifulSoup) -> str:
        """Extract building age."""
        spec_elem = item.find('div', class_='bukkenSpec')
        if spec_elem:
            text = spec_elem.text
            match = re.search(r'築(\d+)年', text)
            if match:
                return f"築{match.group(1)}年"
        return ''
    
    def _extract_floor_info(self, item: BeautifulSoup) -> str:
        """Extract floor information."""
        spec_elem = item.find('div', class_='bukkenSpec')
        if spec_elem:
            text = spec_elem.text
            match = re.search(r'(\d+)階/(\d+)階建', text)
            if match:
                return f"{match.group(1)}階/{match.group(2)}階建"
        return ''
    
    def _extract_station_info(self, item: BeautifulSoup) -> Dict[str, Any]:
        """Extract station information."""
        station_elem = item.find('div', class_='traffic')
        if station_elem:
            text = station_elem.text
            # Extract station name and walking time
            match = re.search(r'(.+?駅)\s*徒歩(\d+)分', text)
            if match:
                return {
                    'name': match.group(1),
                    'distance': f"徒歩{match.group(2)}分"
                }
        return {}