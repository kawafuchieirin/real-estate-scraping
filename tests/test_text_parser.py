"""
Tests for Japanese text parser utility.
"""

import pytest
from src.utils.text_parser import JapaneseTextParser


class TestJapaneseTextParser:
    """Test cases for JapaneseTextParser."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = JapaneseTextParser()
    
    def test_normalize_text(self):
        """Test text normalization."""
        # Full-width to half-width conversion
        assert self.parser.normalize_text("１２３ＡＢＣ") == "123ABC"
        
        # Extra spaces removal
        assert self.parser.normalize_text("  hello   world  ") == "hello world"
        
        # Empty string
        assert self.parser.normalize_text("") == ""
        assert self.parser.normalize_text(None) == ""
    
    def test_parse_rent(self):
        """Test rent parsing."""
        # Standard format
        assert self.parser.parse_rent("8.5万円") == 85000
        assert self.parser.parse_rent("10万円") == 100000
        assert self.parser.parse_rent("12.3万円") == 123000
        
        # With spaces
        assert self.parser.parse_rent("8.5 万円") == 85000
        
        # Full-width numbers
        assert self.parser.parse_rent("８．５万円") == 85000
        
        # Without 円
        assert self.parser.parse_rent("15万") == 150000
        
        # Invalid input
        assert self.parser.parse_rent("") is None
        assert self.parser.parse_rent(None) is None
        assert self.parser.parse_rent("無料") is None
    
    def test_parse_area(self):
        """Test area parsing."""
        # Standard formats
        assert self.parser.parse_area("25.5㎡") == 25.5
        assert self.parser.parse_area("30m²") == 30.0
        assert self.parser.parse_area("40平米") == 40.0
        
        # With spaces
        assert self.parser.parse_area("25.5 ㎡") == 25.5
        
        # Integer area
        assert self.parser.parse_area("35㎡") == 35.0
        
        # Invalid input
        assert self.parser.parse_area("") is None
        assert self.parser.parse_area(None) is None
    
    def test_parse_floor_plan(self):
        """Test floor plan normalization."""
        # Standard formats
        assert self.parser.parse_floor_plan("1LDK") == "1LDK"
        assert self.parser.parse_floor_plan("2DK") == "2DK"
        assert self.parser.parse_floor_plan("3LDK") == "3LDK"
        
        # Full-width
        assert self.parser.parse_floor_plan("１ＬＤＫ") == "1LDK"
        
        # With spaces
        assert self.parser.parse_floor_plan("1 LDK") == "1LDK"
        
        # Lowercase
        assert self.parser.parse_floor_plan("1ldk") == "1LDK"
        
        # Empty
        assert self.parser.parse_floor_plan("") == ""
        assert self.parser.parse_floor_plan(None) == ""
    
    def test_parse_station_distance(self):
        """Test station distance parsing."""
        # Standard formats
        assert self.parser.parse_station_distance("徒歩5分") == 5
        assert self.parser.parse_station_distance("徒歩10分") == 10
        assert self.parser.parse_station_distance("歩15分") == 15
        
        # With spaces
        assert self.parser.parse_station_distance("徒歩 5 分") == 5
        
        # Invalid input
        assert self.parser.parse_station_distance("") is None
        assert self.parser.parse_station_distance(None) is None
        assert self.parser.parse_station_distance("バス10分") is None
    
    def test_parse_building_age(self):
        """Test building age parsing."""
        # Standard formats
        assert self.parser.parse_building_age("築5年") == 5
        assert self.parser.parse_building_age("築10年") == 10
        assert self.parser.parse_building_age("築年数: 15年") == 15
        
        # With spaces
        assert self.parser.parse_building_age("築 5 年") == 5
        
        # Invalid input
        assert self.parser.parse_building_age("") is None
        assert self.parser.parse_building_age(None) is None
        assert self.parser.parse_building_age("新築") is None
    
    def test_parse_floor_info(self):
        """Test floor info parsing."""
        # Standard format
        assert self.parser.parse_floor_info("3階/5階建") == (3, 5)
        assert self.parser.parse_floor_info("10階/20階建") == (10, 20)
        
        # Single floor
        assert self.parser.parse_floor_info("2階") == (2, None)
        assert self.parser.parse_floor_info("3F") == (3, None)
        
        # With spaces
        assert self.parser.parse_floor_info("3 階 / 5 階建") == (3, 5)
        
        # Invalid input
        assert self.parser.parse_floor_info("") == (None, None)
        assert self.parser.parse_floor_info(None) == (None, None)
    
    def test_extract_address_components(self):
        """Test address component extraction."""
        # Full address
        result = self.parser.extract_address_components("東京都渋谷区神宮前1-2-3")
        assert result['prefecture'] == "東京都"
        assert result['city'] == "渋谷区"
        assert result['district'] == "神宮前1-2-3"
        
        # With spaces
        result = self.parser.extract_address_components("東京都 新宿区 西新宿 2-8-1")
        assert result['prefecture'] == "東京都"
        assert result['city'] == "新宿区"
        assert result['district'] == "西新宿"
        assert result['detail'] == "2-8-1"
        
        # Partial address
        result = self.parser.extract_address_components("品川区大崎")
        assert result['prefecture'] == ""
        assert result['city'] == "品川区"
        assert result['district'] == "大崎"
        
        # Empty
        result = self.parser.extract_address_components("")
        assert result['prefecture'] == ""
        assert result['city'] == ""
        assert result['district'] == ""