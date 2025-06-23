"""
Test data processing utilities.
"""

import pytest
import pandas as pd
from src.utils.data_processor import DataProcessor
from src.utils.data_quality import DataQualityChecker


class TestDataProcessor:
    """Test DataProcessor functionality."""
    
    def setup_method(self):
        """Setup test data."""
        self.processor = DataProcessor()
        
    def test_normalize_floor_plan(self):
        """Test floor plan normalization."""
        test_cases = [
            ("１ＬＤＫ", "1LDK"),
            ("1LDK+S", "1LDK"),
            ("2SLDK", "2LDK"),
            ("３ＤＫ", "3DK"),
            ("1LDK", "1LDK"),
            ("", ""),
        ]
        
        for input_val, expected in test_cases:
            result = self.processor.normalize_floor_plan(input_val)
            assert result == expected, f"Failed for {input_val}: got {result}, expected {expected}"
            
    def test_normalize_rent(self):
        """Test rent normalization."""
        test_cases = [
            ("12.5万円", 125000),
            ("125,000円", 125000),
            ("¥125,000", 125000),
            ("125000", 125000),
            ("10万円", 100000),
            ("-", None),
            ("", None),
        ]
        
        for input_val, expected in test_cases:
            result = self.processor.normalize_rent(input_val)
            assert result == expected, f"Failed for {input_val}: got {result}, expected {expected}"
            
    def test_normalize_area(self):
        """Test area normalization."""
        test_cases = [
            ("35.00㎡", 35.0),
            ("35m2", 35.0),
            ("35平米", 35.0),
            ("45.5", 45.5),
            ("-", None),
            ("", None),
        ]
        
        for input_val, expected in test_cases:
            result = self.processor.normalize_area(input_val)
            assert result == expected, f"Failed for {input_val}: got {result}, expected {expected}"
            
    def test_normalize_station_distance(self):
        """Test station distance normalization."""
        test_cases = [
            ("徒歩5分", 5),
            ("駅徒歩10分", 10),
            ("15分", 15),
            ("バス20分", 20),
            ("-", None),
            ("", None),
        ]
        
        for input_val, expected in test_cases:
            result = self.processor.normalize_station_distance(input_val)
            assert result == expected, f"Failed for {input_val}: got {result}, expected {expected}"
            
    def test_normalize_fees(self):
        """Test fee normalization."""
        test_cases = [
            ("1ヶ月", 1),
            ("2ヵ月", 2),
            ("50,000円", 50000),
            ("なし", 0),
            ("-", 0),
            ("無", 0),
            ("", None),
        ]
        
        for input_val, expected in test_cases:
            result = self.processor.normalize_fees(input_val)
            assert result == expected, f"Failed for {input_val}: got {result}, expected {expected}"
            
    def test_process_dataframe(self):
        """Test processing entire DataFrame."""
        data = {
            'floor_plan': ['１ＬＤＫ', '2LDK+S', '３ＤＫ'],
            'rent': ['12.5万円', '20万円', '125,000円'],
            'area': ['35.00㎡', '45m2', '50平米'],
            'station_distance': ['徒歩5分', '10分', 'バス15分'],
            'management_fee': ['5,000円', 'なし', '1ヶ月']
        }
        
        df = pd.DataFrame(data)
        processed_df = self.processor.process_dataframe(df)
        
        # Check normalizations
        assert list(processed_df['floor_plan']) == ['1LDK', '2LDK', '3DK']
        assert list(processed_df['rent']) == [125000, 200000, 125000]
        assert list(processed_df['area']) == [35.0, 45.0, 50.0]
        assert list(processed_df['station_distance']) == [5, 10, 15]
        assert list(processed_df['management_fee']) == [5000, 0, 1]


class TestDataQualityChecker:
    """Test DataQualityChecker functionality."""
    
    def setup_method(self):
        """Setup test data."""
        self.checker = DataQualityChecker()
        
    def test_check_missing_values(self):
        """Test missing value detection."""
        data = {
            'property_id': ['001', '002', None],
            'rent': [100000, 200000, None],
            'area': [30.0, None, 50.0]
        }
        
        df = pd.DataFrame(data)
        report = self.checker.check_data_quality(df)
        
        assert 'property_id' in report['missing_values']
        assert report['missing_values']['property_id']['count'] == 1
        assert report['missing_values']['rent']['count'] == 1
        assert report['missing_values']['area']['count'] == 1
        
    def test_check_outliers(self):
        """Test outlier detection."""
        data = {
            'property_id': ['001', '002', '003'],
            'rent': [100000, 200000, 10000000],  # Last one is outlier
            'area': [30.0, 50.0, 1000.0],  # Last one is outlier
            'floor_number': [5, 10, 150]  # Last one is outlier
        }
        
        df = pd.DataFrame(data)
        report = self.checker.check_data_quality(df)
        
        assert 'rent' in report['outliers']
        assert 'area' in report['outliers']
        assert 'floor_number' in report['outliers']
        
    def test_check_duplicates(self):
        """Test duplicate detection."""
        data = {
            'property_id': ['001', '002', '002'],  # Duplicate
            'url': ['url1', 'url2', 'url2'],  # Duplicate
            'address': ['addr1', 'addr2', 'addr3'],
            'floor_plan': ['1LDK', '2LDK', '1LDK'],
            'rent': [100000, 200000, 150000]
        }
        
        df = pd.DataFrame(data)
        report = self.checker.check_data_quality(df)
        
        assert 'property_id' in report['duplicates']
        assert report['duplicates']['property_id']['count'] == 2
        assert 'url' in report['duplicates']
        assert report['duplicates']['url']['count'] == 2
        
    def test_fix_common_issues(self):
        """Test automatic issue fixing."""
        data = {
            'property_id': ['001', '002', '003', '003'],  # Duplicate
            'rent': [100000, 200000, -1000, 10000000],  # Outliers
            'area': [30.0, 50.0, 0, 1000],  # Outliers
            'latitude': [35.6, 35.7, 100.0, 35.8],  # Invalid
            'longitude': [139.7, 139.8, 200.0, 139.9]  # Invalid
        }
        
        df = pd.DataFrame(data)
        fixed_df = self.checker.fix_common_issues(df)
        
        # Check duplicates removed
        assert len(fixed_df) < len(df)
        
        # Check outliers fixed
        assert fixed_df['rent'].min() >= 10000
        assert fixed_df['rent'].max() <= 5000000
        assert fixed_df['area'].min() >= 5.0
        assert fixed_df['area'].max() <= 500.0
        
        # Check invalid coordinates removed
        assert not ((fixed_df['latitude'] < 24.0) | (fixed_df['latitude'] > 46.0)).any()
        
    def test_quality_score_calculation(self):
        """Test quality score calculation."""
        # Perfect data
        good_data = {
            'property_id': ['001', '002', '003'],
            'site_name': ['SUUMO', 'SUUMO', 'HOMES'],
            'url': ['url1', 'url2', 'url3'],
            'title': ['Title 1', 'Title 2', 'Title 3'],
            'property_type': ['マンション', 'アパート', 'マンション'],
            'city': ['渋谷区', '港区', '世田谷区'],
            'rent': [125000, 200000, 150000],
            'floor_plan': ['1LDK', '2LDK', '1K'],
            'area': [35.5, 50.0, 25.0]
        }
        
        df = pd.DataFrame(good_data)
        report = self.checker.check_data_quality(df)
        
        # Should have high quality score
        assert report['quality_score'] >= 90
        
        # Bad data
        bad_data = good_data.copy()
        bad_data['property_id'] = ['001', '001', None]  # Duplicate and missing
        bad_data['rent'] = [125000, 200000, 10000000]  # Outlier
        
        df_bad = pd.DataFrame(bad_data)
        report_bad = self.checker.check_data_quality(df_bad)
        
        # Should have lower quality score
        assert report_bad['quality_score'] < report['quality_score']