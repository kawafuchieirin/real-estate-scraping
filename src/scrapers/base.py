"""
Base scraper class for real estate websites.
"""

import time
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
import requests
from bs4 import BeautifulSoup
from loguru import logger
from ratelimit import limits, sleep_and_retry

from ..config.settings import settings
from ..models.property import Property, PropertySearchResult


class BaseScraper(ABC):
    """Abstract base class for real estate scrapers."""
    
    def __init__(self, site_name: str, base_url: str):
        self.site_name = site_name
        self.base_url = base_url
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """Create a requests session with appropriate headers."""
        session = requests.Session()
        session.headers.update({
            'User-Agent': settings.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ja,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        return session
    
    @sleep_and_retry
    @limits(calls=settings.RATE_LIMIT_CALLS, period=settings.RATE_LIMIT_PERIOD)
    def _make_request(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Make a rate-limited HTTP request."""
        try:
            logger.info(f"Requesting: {url}")
            response = self.session.get(url, timeout=settings.REQUEST_TIMEOUT, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {str(e)}")
            return None
    
    def _parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content with BeautifulSoup."""
        return BeautifulSoup(html, 'lxml')
    
    def check_robots_txt(self, robots_url: str) -> bool:
        """Check if scraping is allowed according to robots.txt."""
        try:
            response = self._make_request(robots_url)
            if response:
                content = response.text.lower()
                # Simple check - in production, use robotparser
                if 'user-agent: *' in content and 'disallow: /' in content:
                    logger.warning(f"Robots.txt disallows scraping for {self.site_name}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Failed to check robots.txt: {str(e)}")
            return False
    
    @abstractmethod
    def search_properties(
        self,
        area: Dict[str, str],
        property_type: Dict[str, str],
        page: int = 1
    ) -> Optional[PropertySearchResult]:
        """Search for properties in a specific area and type."""
        pass
    
    @abstractmethod
    def parse_property_list(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse property list from search results page."""
        pass
    
    @abstractmethod
    def parse_property_details(self, property_data: Dict[str, Any]) -> Optional[Property]:
        """Parse individual property details."""
        pass
    
    def scrape_area(
        self,
        area: Dict[str, str],
        property_type: Dict[str, str],
        max_pages: int = 5
    ) -> List[Property]:
        """Scrape properties for a specific area and type."""
        all_properties = []
        
        for page in range(1, max_pages + 1):
            logger.info(f"Scraping {self.site_name} - {area['name']} - {property_type['name']} - Page {page}")
            
            result = self.search_properties(area, property_type, page)
            if not result or not result.properties:
                logger.info(f"No more properties found on page {page}")
                break
                
            all_properties.extend(result.properties)
            
            # Be respectful - add delay between pages
            time.sleep(2)
            
        logger.info(f"Total properties scraped: {len(all_properties)}")
        return all_properties