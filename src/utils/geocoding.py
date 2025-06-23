"""
Geocoding utilities for converting addresses to latitude/longitude coordinates.
"""

import os
import time
from typing import Optional, Tuple, Dict, Any
import requests
from loguru import logger
from dotenv import load_dotenv

try:
    import googlemaps
    GOOGLEMAPS_AVAILABLE = True
except ImportError:
    GOOGLEMAPS_AVAILABLE = False
    logger.warning("googlemaps library not available, will use alternative geocoding")

load_dotenv()


class Geocoder:
    """Handle geocoding of addresses to coordinates."""
    
    def __init__(self, provider: str = "google"):
        """
        Initialize geocoder with specified provider.
        
        Args:
            provider: Geocoding provider ('google', 'nominatim')
        """
        self.provider = provider
        self.google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        
        # Initialize Google Maps client if available
        self.gmaps = None
        if self.provider == "google" and self.google_api_key and GOOGLEMAPS_AVAILABLE:
            try:
                self.gmaps = googlemaps.Client(key=self.google_api_key)
                logger.info("Google Maps client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Google Maps client: {e}")
        
        # Rate limiting settings
        self.request_delay = 0.1  # seconds between requests
        self.last_request_time = 0
        
    def geocode(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Geocode an address to latitude/longitude coordinates.
        
        Args:
            address: Address string to geocode
            
        Returns:
            Tuple of (latitude, longitude) or None if failed
        """
        if not address:
            return None
            
        # Apply rate limiting
        self._apply_rate_limit()
        
        try:
            if self.provider == "google" and self.google_api_key:
                return self._geocode_google(address)
            else:
                # Fallback to Nominatim (OpenStreetMap)
                return self._geocode_nominatim(address)
        except Exception as e:
            logger.error(f"Geocoding failed for address '{address}': {e}")
            return None
    
    def _apply_rate_limit(self):
        """Apply rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.request_delay:
            time.sleep(self.request_delay - time_since_last)
            
        self.last_request_time = time.time()
    
    def _geocode_google(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Geocode using Google Maps API.
        
        Args:
            address: Address string to geocode
            
        Returns:
            Tuple of (latitude, longitude) or None if failed
        """
        # Use googlemaps library if available
        if self.gmaps:
            try:
                geocode_result = self.gmaps.geocode(
                    address,
                    language="ja",
                    region="jp"
                )
                
                if geocode_result:
                    location = geocode_result[0]["geometry"]["location"]
                    lat = round(location["lat"], 6)
                    lng = round(location["lng"], 6)
                    
                    logger.debug(f"Google geocoded '{address}' to ({lat}, {lng})")
                    return (lat, lng)
                else:
                    logger.warning(f"Google geocoding failed for '{address}': No results")
                    return None
                    
            except Exception as e:
                logger.error(f"Google geocoding failed: {e}")
                return None
                
        # Fallback to direct API call
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": address,
            "key": self.google_api_key,
            "language": "ja",
            "region": "jp"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data["status"] == "OK" and data["results"]:
                location = data["results"][0]["geometry"]["location"]
                lat = round(location["lat"], 6)
                lng = round(location["lng"], 6)
                
                logger.debug(f"Google geocoded '{address}' to ({lat}, {lng})")
                return (lat, lng)
            else:
                logger.warning(f"Google geocoding failed for '{address}': {data.get('status')}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Google geocoding request failed: {e}")
            return None
    
    def _geocode_nominatim(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Geocode using OpenStreetMap Nominatim (free service).
        
        Args:
            address: Address string to geocode
            
        Returns:
            Tuple of (latitude, longitude) or None if failed
        """
        url = "https://nominatim.openstreetmap.org/search"
        
        # Add country hint for better results
        if "日本" not in address and "Japan" not in address:
            address = f"{address}, 日本"
            
        params = {
            "q": address,
            "format": "json",
            "limit": 1,
            "countrycodes": "jp"
        }
        
        headers = {
            "User-Agent": "RealEstateScraper/1.0"  # Required by Nominatim
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data:
                lat = round(float(data[0]["lat"]), 6)
                lon = round(float(data[0]["lon"]), 6)
                
                logger.debug(f"Nominatim geocoded '{address}' to ({lat}, {lon})")
                return (lat, lon)
            else:
                logger.warning(f"Nominatim geocoding failed for '{address}': No results")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Nominatim geocoding request failed: {e}")
            return None
    
    def batch_geocode(self, addresses: list, progress_callback=None) -> Dict[str, Optional[Tuple[float, float]]]:
        """
        Geocode multiple addresses with progress tracking.
        
        Args:
            addresses: List of addresses to geocode
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Dictionary mapping addresses to coordinates
        """
        results = {}
        total = len(addresses)
        
        for i, address in enumerate(addresses):
            coords = self.geocode(address)
            results[address] = coords
            
            if progress_callback:
                progress_callback(i + 1, total)
                
            # Log progress every 10 addresses
            if (i + 1) % 10 == 0:
                logger.info(f"Geocoded {i + 1}/{total} addresses")
                
        return results
    
    def validate_coordinates(self, lat: float, lon: float) -> bool:
        """
        Validate that coordinates are within reasonable bounds for Japan.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            True if coordinates are valid for Japan
        """
        # Japan's approximate bounds
        japan_bounds = {
            "min_lat": 24.0,
            "max_lat": 46.0,
            "min_lon": 122.0,
            "max_lon": 146.0
        }
        
        return (
            japan_bounds["min_lat"] <= lat <= japan_bounds["max_lat"] and
            japan_bounds["min_lon"] <= lon <= japan_bounds["max_lon"]
        )