"""
Property data models.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class Property(BaseModel):
    """Real estate property model."""
    
    # Basic information
    property_id: str = Field(..., description="Unique property identifier")
    site_name: str = Field(..., description="Source website name")
    url: str = Field(..., description="Property listing URL")
    
    # Property details
    title: str = Field(..., description="Property listing title")
    property_type: str = Field(..., description="Type of property (マンション, アパート, 一戸建て)")
    
    # Location
    prefecture: str = Field(default="東京都", description="Prefecture")
    city: str = Field(..., description="City/Ward")
    district: Optional[str] = Field(None, description="District/Area")
    address: Optional[str] = Field(None, description="Full address")
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")
    
    # Price information
    rent: int = Field(..., description="Monthly rent in JPY")
    management_fee: Optional[int] = Field(None, description="Management fee in JPY")
    deposit: Optional[int] = Field(None, description="Deposit amount in JPY")
    key_money: Optional[int] = Field(None, description="Key money in JPY")
    
    # Property specifications
    floor_plan: str = Field(..., description="Floor plan (1K, 1LDK, etc.)")
    area: float = Field(..., description="Floor area in square meters")
    floor_number: Optional[int] = Field(None, description="Floor number")
    total_floors: Optional[int] = Field(None, description="Total floors in building")
    building_age: Optional[int] = Field(None, description="Building age in years")
    construction_year: Optional[int] = Field(None, description="Year of construction")
    
    # Transportation
    nearest_station: Optional[str] = Field(None, description="Nearest station name")
    station_distance: Optional[int] = Field(None, description="Distance to station in minutes (walking)")
    train_lines: Optional[List[str]] = Field(None, description="Available train lines")
    
    # Additional features
    features: Optional[List[str]] = Field(None, description="Property features")
    
    # Metadata
    scraped_at: datetime = Field(default_factory=datetime.now, description="Timestamp of scraping")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PropertySearchResult(BaseModel):
    """Search result containing multiple properties."""
    
    site_name: str
    search_area: str
    property_type: str
    total_count: int
    page_number: int
    properties: List[Property]
    scraped_at: datetime = Field(default_factory=datetime.now)