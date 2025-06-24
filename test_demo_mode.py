#!/usr/bin/env python
"""
Test script to demonstrate demo mode for scrapers.
Run with: SCRAPER_DEMO_MODE=true python test_demo_mode.py
"""

import os
import sys

# Set demo mode
os.environ['SCRAPER_DEMO_MODE'] = 'true'

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main import main

if __name__ == "__main__":
    print("Running scrapers in DEMO MODE...")
    print("This will return sample data without accessing real websites.")
    print("-" * 60)
    
    # Run main with demo mode enabled
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--areas', nargs='+', default=['13113', '13104'])
    parser.add_argument('--property-types', nargs='+', default=['apartment'])
    parser.add_argument('--export-format', default='csv')
    parser.add_argument('--skip-processing', action='store_true', default=False)
    parser.add_argument('--geocode', action='store_true', default=False)
    parser.add_argument('--upload-s3', action='store_true', default=False)
    
    args = parser.parse_args()
    
    main(args)