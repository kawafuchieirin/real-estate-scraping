"""
Data quality check utilities for validating scraped real estate data.
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from loguru import logger


class DataQualityChecker:
    """Handle data quality validation and reporting."""
    
    def __init__(self):
        # Define validation rules
        self.validation_rules = {
            'rent': {
                'min': 10000,  # 1万円
                'max': 5000000,  # 500万円
                'required': True
            },
            'area': {
                'min': 5.0,  # 5㎡
                'max': 500.0,  # 500㎡
                'required': True
            },
            'floor_number': {
                'min': -3,  # B3F
                'max': 100,  # 100F
                'required': False
            },
            'station_distance': {
                'min': 0,
                'max': 60,  # 60分
                'required': False
            },
            'latitude': {
                'min': 24.0,  # Japan south
                'max': 46.0,  # Japan north
                'required': False
            },
            'longitude': {
                'min': 122.0,  # Japan west
                'max': 146.0,  # Japan east
                'required': False
            }
        }
        
        # Required columns
        self.required_columns = [
            'property_id', 'site_name', 'url', 'title', 
            'property_type', 'city', 'rent', 'floor_plan', 'area'
        ]
        
    def check_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform comprehensive data quality checks.
        
        Args:
            df: DataFrame with property data
            
        Returns:
            Dictionary with quality check results
        """
        report = {
            'total_records': len(df),
            'validation_errors': {},
            'missing_values': {},
            'outliers': {},
            'duplicates': {},
            'summary': {}
        }
        
        # Check for missing required columns
        missing_cols = [col for col in self.required_columns if col not in df.columns]
        if missing_cols:
            report['validation_errors']['missing_columns'] = missing_cols
            
        # Check for missing values
        report['missing_values'] = self._check_missing_values(df)
        
        # Check for outliers and invalid values
        report['outliers'] = self._check_outliers(df)
        
        # Check for duplicates
        report['duplicates'] = self._check_duplicates(df)
        
        # Generate summary statistics
        report['summary'] = self._generate_summary(df)
        
        # Calculate overall quality score
        report['quality_score'] = self._calculate_quality_score(report)
        
        return report
    
    def _check_missing_values(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check for missing values in the dataset."""
        missing_report = {}
        
        for column in df.columns:
            missing_count = df[column].isna().sum()
            missing_pct = (missing_count / len(df)) * 100
            
            if missing_count > 0:
                missing_report[column] = {
                    'count': int(missing_count),
                    'percentage': round(missing_pct, 2)
                }
                
                # Check if required column has missing values
                if column in self.required_columns and missing_count > 0:
                    logger.warning(f"Required column '{column}' has {missing_count} missing values")
                    
        return missing_report
    
    def _check_outliers(self, df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """Check for outliers and invalid values."""
        outliers = {}
        
        for column, rules in self.validation_rules.items():
            if column not in df.columns:
                continue
                
            column_outliers = []
            
            # Check minimum values
            if 'min' in rules:
                below_min = df[df[column] < rules['min']]
                if not below_min.empty:
                    column_outliers.extend([
                        {
                            'index': idx,
                            'value': row[column],
                            'issue': f"Below minimum ({rules['min']})",
                            'property_id': row.get('property_id', 'N/A')
                        }
                        for idx, row in below_min.iterrows()
                    ])
                    
            # Check maximum values
            if 'max' in rules:
                above_max = df[df[column] > rules['max']]
                if not above_max.empty:
                    column_outliers.extend([
                        {
                            'index': idx,
                            'value': row[column],
                            'issue': f"Above maximum ({rules['max']})",
                            'property_id': row.get('property_id', 'N/A')
                        }
                        for idx, row in above_max.iterrows()
                    ])
                    
            if column_outliers:
                outliers[column] = column_outliers[:10]  # Limit to first 10
                
        return outliers
    
    def _check_duplicates(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check for duplicate records."""
        duplicates_report = {}
        
        # Check for duplicate property IDs
        if 'property_id' in df.columns:
            dup_ids = df[df.duplicated(subset=['property_id'], keep=False)]
            if not dup_ids.empty:
                duplicates_report['property_id'] = {
                    'count': len(dup_ids),
                    'examples': dup_ids['property_id'].value_counts().head(5).to_dict()
                }
                
        # Check for duplicate URLs
        if 'url' in df.columns:
            dup_urls = df[df.duplicated(subset=['url'], keep=False)]
            if not dup_urls.empty:
                duplicates_report['url'] = {
                    'count': len(dup_urls),
                    'examples': dup_urls['url'].value_counts().head(5).to_dict()
                }
                
        # Check for potential duplicate properties (same address and floor plan)
        if all(col in df.columns for col in ['address', 'floor_plan', 'rent']):
            dup_props = df[df.duplicated(subset=['address', 'floor_plan', 'rent'], keep=False)]
            if not dup_props.empty:
                duplicates_report['potential_duplicates'] = {
                    'count': len(dup_props),
                    'percentage': round((len(dup_props) / len(df)) * 100, 2)
                }
                
        return duplicates_report
    
    def _generate_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics for the dataset."""
        summary = {
            'total_records': len(df),
            'columns': list(df.columns),
            'data_types': df.dtypes.astype(str).to_dict()
        }
        
        # Numeric column statistics
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            summary['numeric_stats'] = {}
            for col in numeric_columns:
                if col in df.columns and df[col].notna().any():
                    summary['numeric_stats'][col] = {
                        'mean': round(df[col].mean(), 2),
                        'median': round(df[col].median(), 2),
                        'std': round(df[col].std(), 2),
                        'min': round(df[col].min(), 2),
                        'max': round(df[col].max(), 2)
                    }
                    
        # Categorical column statistics
        categorical_columns = ['property_type', 'city', 'floor_plan', 'site_name']
        summary['categorical_stats'] = {}
        for col in categorical_columns:
            if col in df.columns:
                value_counts = df[col].value_counts()
                summary['categorical_stats'][col] = {
                    'unique_values': len(value_counts),
                    'top_values': value_counts.head(5).to_dict()
                }
                
        return summary
    
    def _calculate_quality_score(self, report: Dict[str, Any]) -> float:
        """
        Calculate overall data quality score (0-100).
        
        Args:
            report: Quality check report
            
        Returns:
            Quality score between 0 and 100
        """
        score = 100.0
        
        # Deduct points for missing values in required fields
        for col in self.required_columns:
            if col in report['missing_values']:
                score -= min(10, report['missing_values'][col]['percentage'])
                
        # Deduct points for outliers
        outlier_penalty = min(20, len(report['outliers']) * 2)
        score -= outlier_penalty
        
        # Deduct points for duplicates
        if 'property_id' in report['duplicates']:
            score -= 10
        if 'url' in report['duplicates']:
            score -= 5
            
        # Ensure score is between 0 and 100
        return max(0, min(100, score))
    
    def fix_common_issues(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fix common data quality issues automatically.
        
        Args:
            df: DataFrame with property data
            
        Returns:
            Cleaned DataFrame
        """
        df = df.copy()
        
        # Remove complete duplicates
        df = df.drop_duplicates()
        
        # Remove records with missing required values
        for col in self.required_columns:
            if col in df.columns:
                df = df[df[col].notna()]
                
        # Fix outliers by capping values
        for column, rules in self.validation_rules.items():
            if column not in df.columns:
                continue
                
            if 'min' in rules and 'max' in rules:
                df[column] = df[column].clip(lower=rules['min'], upper=rules['max'])
                
        # Remove records with invalid coordinates
        if 'latitude' in df.columns and 'longitude' in df.columns:
            valid_coords = (
                (df['latitude'] >= 24.0) & (df['latitude'] <= 46.0) &
                (df['longitude'] >= 122.0) & (df['longitude'] <= 146.0)
            )
            invalid_count = (~valid_coords).sum()
            if invalid_count > 0:
                logger.warning(f"Removing {invalid_count} records with invalid coordinates")
                df = df[valid_coords | df['latitude'].isna() | df['longitude'].isna()]
                
        logger.info(f"Data quality fixes applied. Final record count: {len(df)}")
        return df
    
    def generate_quality_report_html(self, report: Dict[str, Any]) -> str:
        """
        Generate an HTML report for data quality results.
        
        Args:
            report: Quality check report
            
        Returns:
            HTML string
        """
        html = f"""
        <html>
        <head>
            <title>Data Quality Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2, h3 {{ color: #333; }}
                .score {{ font-size: 24px; font-weight: bold; }}
                .good {{ color: green; }}
                .warning {{ color: orange; }}
                .bad {{ color: red; }}
                table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Data Quality Report</h1>
            
            <h2>Overall Quality Score: 
                <span class="score {'good' if report['quality_score'] >= 80 else 'warning' if report['quality_score'] >= 60 else 'bad'}">
                    {report['quality_score']:.1f}/100
                </span>
            </h2>
            
            <h3>Summary</h3>
            <p>Total Records: {report['total_records']}</p>
            
            <h3>Missing Values</h3>
            <table>
                <tr><th>Column</th><th>Missing Count</th><th>Percentage</th></tr>
                {''.join(f"<tr><td>{col}</td><td>{info['count']}</td><td>{info['percentage']}%</td></tr>" 
                         for col, info in report['missing_values'].items())}
            </table>
            
            <h3>Outliers</h3>
            <table>
                <tr><th>Column</th><th>Issue Count</th><th>Examples</th></tr>
                {''.join(f"<tr><td>{col}</td><td>{len(outliers)}</td><td>{outliers[0]['issue'] if outliers else ''}</td></tr>" 
                         for col, outliers in report['outliers'].items())}
            </table>
            
            <h3>Duplicates</h3>
            <table>
                <tr><th>Type</th><th>Count</th></tr>
                {''.join(f"<tr><td>{dtype}</td><td>{info['count']}</td></tr>" 
                         for dtype, info in report['duplicates'].items())}
            </table>
        </body>
        </html>
        """
        
        return html