"""
Robots.txt parser utility.
"""

import urllib.robotparser
from urllib.parse import urljoin, urlparse
from typing import Optional
import requests
from loguru import logger

from ..config.settings import settings


class RobotsChecker:
    """Check robots.txt compliance for web scraping."""
    
    def __init__(self, user_agent: str = None):
        self.user_agent = user_agent or settings.USER_AGENT
        self.parsers = {}  # Cache parsers by domain
    
    def can_fetch(self, url: str) -> bool:
        """
        Check if URL can be fetched according to robots.txt.
        
        Args:
            url: The URL to check
            
        Returns:
            True if fetching is allowed, False otherwise
        """
        try:
            # Parse URL to get domain
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            
            # Check cache
            if base_url not in self.parsers:
                self._load_robots_txt(base_url)
            
            # Check if URL is allowed
            if base_url in self.parsers and self.parsers[base_url]:
                return self.parsers[base_url].can_fetch(self.user_agent, url)
            
            # If no robots.txt or error, allow by default
            return True
            
        except Exception as e:
            logger.error(f"Error checking robots.txt for {url}: {str(e)}")
            return True  # Allow on error
    
    def _load_robots_txt(self, base_url: str) -> None:
        """Load and parse robots.txt for a domain."""
        robots_url = urljoin(base_url, '/robots.txt')
        
        try:
            logger.info(f"Fetching robots.txt from {robots_url}")
            
            # Create parser
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)
            
            # Fetch robots.txt with timeout
            response = requests.get(
                robots_url,
                timeout=settings.REQUEST_TIMEOUT,
                headers={'User-Agent': self.user_agent}
            )
            
            if response.status_code == 200:
                # Parse robots.txt content
                rp.parse(response.text.splitlines())
                self.parsers[base_url] = rp
                logger.info(f"Successfully loaded robots.txt for {base_url}")
            else:
                logger.warning(f"No robots.txt found at {robots_url} (status: {response.status_code})")
                self.parsers[base_url] = None
                
        except Exception as e:
            logger.error(f"Failed to load robots.txt from {robots_url}: {str(e)}")
            self.parsers[base_url] = None
    
    def get_crawl_delay(self, url: str) -> Optional[float]:
        """
        Get crawl delay from robots.txt.
        
        Args:
            url: The URL to check
            
        Returns:
            Crawl delay in seconds, or None if not specified
        """
        try:
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            
            if base_url not in self.parsers:
                self._load_robots_txt(base_url)
            
            if base_url in self.parsers and self.parsers[base_url]:
                delay = self.parsers[base_url].crawl_delay(self.user_agent)
                return float(delay) if delay else None
                
        except Exception as e:
            logger.error(f"Error getting crawl delay for {url}: {str(e)}")
            
        return None
    
    def get_request_rate(self, url: str) -> Optional[tuple]:
        """
        Get request rate from robots.txt.
        
        Args:
            url: The URL to check
            
        Returns:
            Tuple of (requests, seconds) or None if not specified
        """
        try:
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            
            if base_url not in self.parsers:
                self._load_robots_txt(base_url)
            
            if base_url in self.parsers and self.parsers[base_url]:
                rate = self.parsers[base_url].request_rate(self.user_agent)
                if rate:
                    return (rate.requests, rate.seconds)
                    
        except Exception as e:
            logger.error(f"Error getting request rate for {url}: {str(e)}")
            
        return None