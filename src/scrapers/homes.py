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
from .demo_data import generate_demo_properties, is_demo_mode_enabled


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
        # Check if demo mode is enabled
        if is_demo_mode_enabled():
            logger.info("Demo mode enabled - returning demo data")
            demo_properties = generate_demo_properties("HOMES", area['code'], property_type['code'])
            return PropertySearchResult(
                properties=[self._convert_demo_to_property(p) for p in demo_properties],
                total_count=len(demo_properties),
                has_next_page=False
            )
        
        # Map property types to HOMES format
        type_mapping = {
            'apartment': '1101',  # マンション
            'apart': '1103',      # アパート
            'house': '1201'       # 一戸建て
        }
        
        property_type_code = type_mapping.get(property_type['code'], '1101')
        
        # Construct search URL with correct HOMES format
        # HOMES uses a different URL structure with parameters
        search_url = f"{self.base_url}/chintai/tokyo/city/{area['code']}-t/"
        
        # Build query parameters
        params = {
            'bek': property_type_code,  # Building type code
            'p': page                    # Page number
        }
        
        logger.info(f"Searching HOMES at: {search_url} with params: {params}")
            
        response = self._make_request(search_url, params=params)
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
        
        # Look for property items with multiple possible selectors
        property_items = soup.find_all('div', class_='bukkenList')
        if not property_items:
            property_items = soup.find_all('div', class_='propertyBlock')
        if not property_items:
            property_items = soup.find_all('article', class_='property-item')
        
        if not property_items:
            logger.info("No properties found. Checking if page structure changed.")
            # Try to find any common property container patterns
            property_items = soup.find_all('div', {'class': re.compile(r'property|bukken|item', re.I)})[:20]
            
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
        # Try multiple possible link selectors
        link = item.find('a', class_='bukkenName')
        if not link:
            link = item.find('a', class_='property-link')
        if not link:
            link = item.find('a', href=re.compile(r'/chintai/.*/'))
        
        if link and link.get('href'):
            href = link['href']
            if href.startswith('http'):
                return href
            return self.base_url + href
        return ''
    
    def _extract_title(self, item: BeautifulSoup) -> str:
        """Extract property title."""
        # Try multiple possible title selectors
        title_elem = item.find('h2', class_='bukkenName')
        if not title_elem:
            title_elem = item.find('h3', class_='property-title')
        if not title_elem:
            title_elem = item.find(['h2', 'h3'], text=re.compile(r'.{5,}'))  # At least 5 chars
        return title_elem.text.strip() if title_elem else ''
    
    def _extract_rent(self, item: BeautifulSoup) -> str:
        """Extract rent amount."""
        # Try multiple possible rent selectors
        rent_elem = item.find('span', class_='priceLabel')
        if not rent_elem:
            rent_elem = item.find('span', class_='price')
        if not rent_elem:
            rent_elem = item.find('div', class_='rent')
        if not rent_elem:
            # Look for text containing 万円
            rent_elem = item.find(text=re.compile(r'\d+\.?\d*万円'))
            if rent_elem:
                return rent_elem.strip()
        return rent_elem.text.strip() if rent_elem else '0'
    
    def _extract_floor_plan(self, item: BeautifulSoup) -> str:
        """Extract floor plan."""
        # Try multiple possible floor plan selectors
        plan_elem = item.find('span', class_='layout')
        if not plan_elem:
            plan_elem = item.find('span', class_='madori')
        if not plan_elem:
            # Look for text containing common floor plan patterns
            plan_elem = item.find(text=re.compile(r'\d[LDK]|ワンルーム'))
            if plan_elem:
                return plan_elem.strip()
        return plan_elem.text.strip() if plan_elem else ''
    
    def _extract_area(self, item: BeautifulSoup) -> str:
        """Extract property area."""
        # Try multiple possible area selectors
        area_elem = item.find('span', class_='space')
        if not area_elem:
            area_elem = item.find('span', class_='menseki')
        if not area_elem:
            # Look for text containing m²
            area_elem = item.find(text=re.compile(r'\d+\.?\d*m²|\d+\.?\d*㎡'))
            if area_elem:
                return area_elem.strip()
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
    
    def _convert_demo_to_property(self, demo_data: Dict[str, Any]) -> Property:
        """Convert demo data to Property model."""
        return Property(
            id=demo_data['id'],
            url=demo_data['url'],
            title=demo_data['title'],
            rent=demo_data['rent'],
            floor_plan=demo_data['floor_plan'],
            area=demo_data['area'],
            address=demo_data['address'],
            station_info=demo_data['station_info'],
            building_age=demo_data.get('building_age'),
            floor_info=demo_data.get('floor_info'),
            management_fee=demo_data.get('management_fee'),
            deposit=demo_data.get('deposit'),
            key_money=demo_data.get('key_money'),
            scraped_at=datetime.fromisoformat(demo_data['scraped_at']),
            source=demo_data['source']
        )