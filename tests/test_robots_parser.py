"""
Tests for robots.txt parser utility.
"""

import pytest
from unittest.mock import Mock, patch
from src.utils.robots_parser import RobotsChecker


class TestRobotsChecker:
    """Test cases for RobotsChecker."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.checker = RobotsChecker("TestBot/1.0")
    
    @patch('requests.get')
    def test_can_fetch_allowed(self, mock_get):
        """Test URL that is allowed by robots.txt."""
        # Mock robots.txt content
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
User-agent: *
Allow: /chintai/
Disallow: /admin/
"""
        mock_get.return_value = mock_response
        
        # Test allowed URL
        assert self.checker.can_fetch("https://example.com/chintai/tokyo/") is True
        
    @patch('requests.get')
    def test_can_fetch_disallowed(self, mock_get):
        """Test URL that is disallowed by robots.txt."""
        # Mock robots.txt content
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
User-agent: *
Disallow: /admin/
Disallow: /private/
"""
        mock_get.return_value = mock_response
        
        # Test disallowed URL
        assert self.checker.can_fetch("https://example.com/admin/") is False
        
    @patch('requests.get')
    def test_can_fetch_no_robots(self, mock_get):
        """Test when robots.txt doesn't exist."""
        # Mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # Should allow when no robots.txt
        assert self.checker.can_fetch("https://example.com/page/") is True
        
    @patch('requests.get')
    def test_can_fetch_error(self, mock_get):
        """Test error handling."""
        # Mock network error
        mock_get.side_effect = Exception("Network error")
        
        # Should allow on error
        assert self.checker.can_fetch("https://example.com/page/") is True
        
    @patch('requests.get')
    def test_get_crawl_delay(self, mock_get):
        """Test crawl delay extraction."""
        # Mock robots.txt with crawl delay
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
User-agent: *
Crawl-delay: 2.5
Allow: /
"""
        mock_get.return_value = mock_response
        
        # Test crawl delay
        delay = self.checker.get_crawl_delay("https://example.com/")
        assert delay == 2.5
        
    @patch('requests.get')
    def test_get_crawl_delay_none(self, mock_get):
        """Test when no crawl delay is specified."""
        # Mock robots.txt without crawl delay
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
User-agent: *
Allow: /
"""
        mock_get.return_value = mock_response
        
        # Test no crawl delay
        delay = self.checker.get_crawl_delay("https://example.com/")
        assert delay is None
        
    def test_cache_behavior(self):
        """Test that robots.txt is cached per domain."""
        with patch('requests.get') as mock_get:
            # Mock response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "User-agent: *\nAllow: /"
            mock_get.return_value = mock_response
            
            # First call
            self.checker.can_fetch("https://example.com/page1/")
            assert mock_get.call_count == 1
            
            # Second call to same domain should use cache
            self.checker.can_fetch("https://example.com/page2/")
            assert mock_get.call_count == 1
            
            # Different domain should make new request
            self.checker.can_fetch("https://other.com/page/")
            assert mock_get.call_count == 2