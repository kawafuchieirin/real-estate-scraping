"""
SUUMO real estate website scraper.
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


class SuumoScraper(BaseScraper):
    """Scraper for SUUMO real estate website."""
    
    def __init__(self):
        super().__init__(
            site_name="SUUMO",
            base_url="https://suumo.jp"
        )
        self.parser = JapaneseTextParser()
        
    def _build_search_params(self, area_code: str, page: int = 1) -> Dict[str, Any]:
        """Build search query parameters for SUUMO.
        
        Args:
            area_code: Area code (e.g., '13113' for Shibuya)
            page: Page number (default: 1)
            
        Returns:
            Dictionary of query parameters
        """
        return {
            'ar': '030',        # 地域コード（首都圏）
            'bs': '010',        # 種別コード（賃貸）
            'ta': '13',         # 都道府県コード（東京都）
            'sc': area_code,    # 市区町村コード
            'page': page        # ページ番号
        }
    
    def search_properties(
        self,
        area: Dict[str, str],
        property_type: Dict[str, str],
        page: int = 1
    ) -> Optional[PropertySearchResult]:
        """Search for properties on SUUMO."""
        # Check if demo mode is enabled
        if is_demo_mode_enabled():
            logger.info("Demo mode enabled - returning demo data")
            demo_properties = generate_demo_properties("SUUMO", area['code'], property_type['code'])
            return PropertySearchResult(
                properties=[self._convert_demo_to_property(p) for p in demo_properties],
                total_count=len(demo_properties),
                has_next_page=False
            )
        
        # Note: Using new parameter-based URL format
        
        area_code = area['code']
        
        # Build search URL with new format
        search_url = f"{self.base_url}/jj/bukken/ichiran/JJ011FC001/"
        
        # Check robots.txt compliance for new URL path
        if not self.robots_checker.can_fetch(search_url):
            logger.warning(f"Robots.txt disallows fetching {search_url}")
            return None
        
        # Build query parameters
        params = self._build_search_params(area_code, page)
        logger.debug(f"Searching SUUMO with params: {params}")
            
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
        """Parse property list from SUUMO search results."""
        properties = []
        
        # Look for property items with multiple possible selectors
        property_items = soup.find_all('div', class_='cassetteitem')
        if not property_items:
            property_items = soup.find_all('div', class_='property_unit')
        if not property_items:
            property_items = soup.find_all('div', {'class': re.compile(r'js-cassette_link')})
        
        if not property_items:
            logger.info("No properties found with standard selectors. Trying alternative patterns.")
            # Try to find property containers
            property_items = soup.find_all('div', {'class': re.compile(r'cassette|property|item', re.I)})[:20]
            
        for item in property_items:
            try:
                prop_data = {
                    'url': self._extract_url(item),
                    'title': self._extract_title(item),
                    'rent': self._extract_price(item),
                    'floor_plan': self._extract_floor_plan(item),
                    'area': self._extract_area(item),
                    'address': self._extract_address(item),
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
            property_id = f"suumo_{hash(property_data.get('url', ''))}"
            
            # Use parser for normalization
            rent = self.parser.parse_rent(property_data.get('rent', ''))
            area = self.parser.parse_area(property_data.get('area', ''))
            floor_plan = self.parser.parse_floor_plan(property_data.get('floor_plan', ''))
            
            # Parse station distance
            station_distance = None
            if property_data.get('station_info', {}).get('distance'):
                station_distance = self.parser.parse_station_distance(
                    property_data['station_info']['distance']
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
                property_type="マンション",  # Would need to be determined from page
                prefecture=address_components.get('prefecture', '東京都'),
                city=address_components.get('city', ''),
                district=address_components.get('district'),
                address=property_data.get('address', ''),
                rent=rent or 0,
                floor_plan=floor_plan,
                area=area or 0.0,
                nearest_station=property_data.get('station_info', {}).get('name'),
                station_distance=station_distance
            )
        except Exception as e:
            logger.error(f"Error creating property object: {str(e)}")
            return None
    
    def _extract_url(self, item: BeautifulSoup) -> str:
        """Extract property URL."""
        # Try multiple possible link selectors
        link = item.find('a', class_='js-cassette_link_href')
        if not link:
            link = item.find('a', class_='js-property_link')
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
        title_elem = item.find('div', class_='cassetteitem_content-title')
        if not title_elem:
            title_elem = item.find('h2', class_='property-title')
        if not title_elem:
            title_elem = item.find(['h2', 'h3'], text=re.compile(r'.{5,}'))  # At least 5 chars
        return title_elem.text.strip() if title_elem else ''
    
    def _extract_price(self, item: BeautifulSoup) -> str:
        """Extract price from property item."""
        # Try multiple possible price selectors
        price_elem = item.find('span', class_='cassetteitem_price--rent')
        if not price_elem:
            price_elem = item.find('span', class_='ui-text--bold')
        if not price_elem:
            price_elem = item.find('div', class_='cassetteitem_other-emphasis')
        if not price_elem:
            # Look for text containing 万円
            price_elem = item.find(text=re.compile(r'\d+\.?\d*万円'))
            if price_elem:
                return price_elem.strip()
        return price_elem.text.strip() if price_elem else '0'
    
    def _extract_floor_plan(self, item: BeautifulSoup) -> str:
        """Extract floor plan from property item."""
        # Try multiple possible floor plan selectors
        plan_elem = item.find('span', class_='cassetteitem_madori')
        if not plan_elem:
            plan_elem = item.find('td', class_='cassetteitem_madori')
        if not plan_elem:
            # Look for text containing common floor plan patterns
            plan_elem = item.find(text=re.compile(r'\d[LDK]|\d[SLDK]|ワンルーム'))
            if plan_elem:
                return plan_elem.strip()
        return plan_elem.text.strip() if plan_elem else ''
    
    def _extract_area(self, item: BeautifulSoup) -> str:
        """Extract area from property item."""
        # Try multiple possible area selectors
        area_elem = item.find('span', class_='cassetteitem_menseki')
        if not area_elem:
            area_elem = item.find('td', class_='cassetteitem_menseki')
        if not area_elem:
            # Look for text containing m²
            area_elem = item.find(text=re.compile(r'\d+\.?\d*m²|\d+\.?\d*㎡'))
            if area_elem:
                return area_elem.strip()
        return area_elem.text.strip() if area_elem else '0'
    
    def _extract_address(self, item: BeautifulSoup) -> str:
        """Extract address from property item."""
        # Try multiple possible address selectors
        addr_elem = item.find('div', class_='cassetteitem_detail-col1')
        if not addr_elem:
            addr_elem = item.find('td', class_='cassetteitem_detail-col1')
        if not addr_elem:
            # Look for text containing 東京都
            addr_elem = item.find(text=re.compile(r'東京都.*[区市]'))
            if addr_elem:
                return addr_elem.strip()
        return addr_elem.text.strip() if addr_elem else ''
    
    def _extract_station_info(self, item: BeautifulSoup) -> Dict[str, Any]:
        """Extract station information from property item."""
        # Try multiple possible station info selectors
        station_elem = item.find('div', class_='cassetteitem_detail-text')
        if not station_elem:
            station_elem = item.find('div', class_='cassetteitem_detail-col2')
        
        if station_elem:
            text = station_elem.text
            # Extract station name and walking time
            match = re.search(r'(.+?駅?).*?歩(\d+)分', text)
            if match:
                return {
                    'name': match.group(1).strip(),
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