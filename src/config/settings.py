"""
Configuration settings for the real estate scraping project.
"""

from typing import List, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field


class TargetSite:
    """Target website configuration."""
    def __init__(self, name: str, base_url: str, search_url: str, robots_txt: str):
        self.name = name
        self.base_url = base_url
        self.search_url = search_url
        self.robots_txt = robots_txt


class Settings(BaseSettings):
    """Project settings."""
    
    # Target sites configuration
    TARGET_SITES: List[Dict[str, str]] = [
        {
            "name": "SUUMO",
            "base_url": "https://suumo.jp",
            "search_url": "https://suumo.jp/chintai/tokyo/city/",
            "robots_txt": "https://suumo.jp/robots.txt"
        },
        {
            "name": "HOMES",
            "base_url": "https://www.homes.co.jp",
            "search_url": "https://www.homes.co.jp/chintai/tokyo/",
            "robots_txt": "https://www.homes.co.jp/robots.txt"
        }
    ]
    
    # Target areas (Tokyo 23 wards)
    TARGET_AREAS: List[Dict[str, str]] = [
        {"code": "13101", "name": "千代田区"},
        {"code": "13102", "name": "中央区"},
        {"code": "13103", "name": "港区"},
        {"code": "13104", "name": "新宿区"},
        {"code": "13105", "name": "文京区"},
        {"code": "13106", "name": "台東区"},
        {"code": "13107", "name": "墨田区"},
        {"code": "13108", "name": "江東区"},
        {"code": "13109", "name": "品川区"},
        {"code": "13110", "name": "目黒区"},
        {"code": "13111", "name": "大田区"},
        {"code": "13112", "name": "世田谷区"},
        {"code": "13113", "name": "渋谷区"},
        {"code": "13114", "name": "中野区"},
        {"code": "13115", "name": "杉並区"},
        {"code": "13116", "name": "豊島区"},
        {"code": "13117", "name": "北区"},
        {"code": "13118", "name": "荒川区"},
        {"code": "13119", "name": "板橋区"},
        {"code": "13120", "name": "練馬区"},
        {"code": "13121", "name": "足立区"},
        {"code": "13122", "name": "葛飾区"},
        {"code": "13123", "name": "江戸川区"}
    ]
    
    # Property types
    PROPERTY_TYPES: List[Dict[str, str]] = [
        {"code": "apartment", "name": "マンション"},
        {"code": "apart", "name": "アパート"},
        {"code": "house", "name": "一戸建て"}
    ]
    
    # Scraping settings
    REQUEST_TIMEOUT: int = Field(default=30, description="Request timeout in seconds")
    RATE_LIMIT_CALLS: int = Field(default=10, description="Number of calls allowed")
    RATE_LIMIT_PERIOD: int = Field(default=60, description="Rate limit period in seconds")
    USER_AGENT: str = Field(
        default="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        description="User agent for requests"
    )
    
    # Storage settings
    DATA_DIR: str = Field(default="data", description="Data directory path")
    RAW_DATA_DIR: str = Field(default="data/raw", description="Raw data directory")
    PROCESSED_DATA_DIR: str = Field(default="data/processed", description="Processed data directory")
    LOG_DIR: str = Field(default="logs", description="Log directory")
    
    # AWS settings (for future use)
    AWS_REGION: str = Field(default="ap-northeast-1", description="AWS region")
    S3_BUCKET_NAME: str = Field(default="", description="S3 bucket name")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Create global settings instance
settings = Settings()