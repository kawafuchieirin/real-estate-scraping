"""
Demo data for testing scrapers without real website selectors.
"""
from typing import List, Dict, Any
import random
from datetime import datetime, timedelta

def generate_demo_properties(site: str, area_code: str, property_type: str, count: int = 5) -> List[Dict[str, Any]]:
    """Generate demo property data for testing."""
    properties = []
    
    # Area names mapping
    area_names = {
        "13113": "渋谷区",
        "13104": "新宿区",
        "13103": "港区",
        "13112": "世田谷区"
    }
    
    area_name = area_names.get(area_code, "東京都")
    
    for i in range(count):
        # Generate random property data
        rent = random.randint(8, 30) * 10000  # 80,000 - 300,000 yen
        size = random.randint(20, 80)  # 20-80 m²
        
        floor_plans = ["1K", "1DK", "1LDK", "2K", "2DK", "2LDK", "3LDK"]
        floor_plan = random.choice(floor_plans)
        
        # Generate building age
        built_year = datetime.now().year - random.randint(0, 30)
        
        # Station info
        stations = ["渋谷", "新宿", "恵比寿", "原宿", "代々木", "品川"]
        station = random.choice(stations)
        walk_time = random.randint(3, 15)
        
        prop = {
            'id': f"{site.lower()}_demo_{area_code}_{i+1}",
            'url': f"https://example.com/property/{i+1}",
            'title': f"デモ物件 {area_name} {floor_plan} - {site}",
            'rent': rent,
            'floor_plan': floor_plan,
            'area': size,
            'address': f"{area_name} デモ町 {random.randint(1, 5)}-{random.randint(1, 20)}-{random.randint(1, 10)}",
            'station_info': [f"{station}駅 徒歩{walk_time}分"],
            'building_age': f"{datetime.now().year - built_year}年",
            'floor_info': f"{random.randint(1, 10)}階",
            'management_fee': random.randint(0, 15000),
            'deposit': rent // 10000,  # 1 month
            'key_money': random.randint(0, 2) * (rent // 10000),  # 0-2 months
            'scraped_at': datetime.now().isoformat(),
            'source': site
        }
        
        properties.append(prop)
    
    return properties

def is_demo_mode_enabled() -> bool:
    """Check if demo mode is enabled via environment variable."""
    import os
    return os.environ.get('SCRAPER_DEMO_MODE', '').lower() == 'true'