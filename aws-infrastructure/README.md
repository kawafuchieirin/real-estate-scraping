# AWS Infrastructure for Real Estate Data Analysis

This directory contains AWS CloudFormation templates and resources for setting up a Glue + Athena analytics infrastructure for the real estate data stored in S3.

## Overview

The infrastructure provides:
- AWS Glue Database and Crawler for automatic schema discovery
- Explicit table definitions for both Parquet and CSV formats
- Pre-configured Athena workgroup for query execution
- Sample SQL queries for common analysis patterns
- Support for partitioned data by date

## Architecture

```
S3 Bucket (real-estate-data)
    ├── cleaned/
    │   └── tokyo/
    │       ├── year=2024/month=01/day=01/
    │       │   └── *.parquet
    │       └── year=2024/month=01/day=02/
    │           └── *.parquet
    └── athena-results/
        └── (query results)
                ↓
        Glue Crawler
                ↓
        Glue Database
                ↓
        Athena Queries
                ↓
    Analysis Results
```

## Files

### CloudFormation Templates

1. **glue-athena-stack.yaml** - Main infrastructure stack
   - Glue Database
   - Glue Crawler with IAM role
   - Athena Workgroup
   - Pre-defined Named Queries

2. **glue-table-schema.yaml** - Explicit table definitions
   - Parquet table schema
   - CSV table schema (alternative)
   - Field mapping documentation

### Athena Query Examples

Located in `athena-queries/`:
- `01_average_rent_by_ward.sql` - Average rent statistics by Tokyo ward
- `02_station_distance_analysis.sql` - Analysis by walking distance to station
- `03_building_age_distribution.sql` - Property distribution by building age
- `04_floor_plan_analysis.sql` - Analysis by floor plan type
- `05_price_per_sqm_by_location.sql` - Rent efficiency by location
- `06_comprehensive_property_analysis.sql` - Multi-dimensional analysis
- `07_time_series_analysis.sql` - Trends over time
- `08_best_value_properties.sql` - Find best value properties

## Deployment Guide

### Prerequisites

1. AWS CLI configured with appropriate credentials
2. S3 bucket with real estate data
3. Appropriate IAM permissions for CloudFormation

### Step 1: Deploy Main Infrastructure

```bash
aws cloudformation create-stack \
  --stack-name real-estate-glue-athena \
  --template-body file://glue-athena-stack.yaml \
  --parameters \
    ParameterKey=S3BucketName,ParameterValue=your-bucket-name \
    ParameterKey=DataPrefix,ParameterValue=cleaned/tokyo/ \
  --capabilities CAPABILITY_NAMED_IAM
```

### Step 2: Deploy Table Schema (Optional)

If you want explicit table definitions instead of relying on the crawler:

```bash
aws cloudformation create-stack \
  --stack-name real-estate-table-schema \
  --template-body file://glue-table-schema.yaml \
  --parameters \
    ParameterKey=S3BucketName,ParameterValue=your-bucket-name \
    ParameterKey=GlueDatabaseName,ParameterValue=real_estate_db
```

### Step 3: Run the Crawler

After deployment, run the crawler to discover your data:

```bash
aws glue start-crawler --name real-estate-crawler
```

Check crawler status:

```bash
aws glue get-crawler --name real-estate-crawler
```

### Step 4: Verify Tables

List tables in the database:

```bash
aws glue get-tables --database-name real_estate_db
```

## Using Athena

### Via AWS Console

1. Open Athena Console
2. Select workgroup: `real-estate-analysis`
3. Select database: `real_estate_db`
4. Run queries from the `athena-queries/` directory

### Via AWS CLI

```bash
# Start query execution
aws athena start-query-execution \
  --query-string "SELECT COUNT(*) FROM real_estate_db.tokyo_properties" \
  --work-group real-estate-analysis \
  --query-execution-context Database=real_estate_db

# Get query results
aws athena get-query-results --query-execution-id <execution-id>
```

### Via Python (boto3)

```python
import boto3
import time

athena = boto3.client('athena')

# Execute query
response = athena.start_query_execution(
    QueryString='SELECT city, AVG(rent) as avg_rent FROM real_estate_db.tokyo_properties GROUP BY city',
    QueryExecutionContext={'Database': 'real_estate_db'},
    WorkGroup='real-estate-analysis'
)

query_execution_id = response['QueryExecutionId']

# Wait for completion
while True:
    result = athena.get_query_execution(QueryExecutionId=query_execution_id)
    status = result['QueryExecution']['Status']['State']
    
    if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
        break
    time.sleep(1)

# Get results
if status == 'SUCCEEDED':
    results = athena.get_query_results(QueryExecutionId=query_execution_id)
    # Process results...
```

## Field Mapping Reference

The table schema maps the issue requirements to actual field names:

| Requirement | Actual Field | Type |
|-------------|--------------|------|
| price | rent | int |
| area | area | float |
| layout | floor_plan | string |
| year_built | construction_year | int |
| walk_time_to_station | station_distance | int |
| latitude | latitude | float |
| longitude | longitude | float |
| date | scraped_at | timestamp |
| address | address | string |

## Cost Optimization

1. **Data Format**: Use Parquet format with Snappy compression
2. **Partitioning**: Data is partitioned by year/month/day
3. **Query Optimization**: 
   - Use partition filters: `WHERE year='2024' AND month='01'`
   - Limit data scanned with column selection
   - Use LIMIT for exploratory queries

## Integration with Other Services

### QuickSight

1. Create a QuickSight data source pointing to Athena
2. Use the `real_estate_db` database
3. Create visualizations based on the queries

### SageMaker

```python
# Example: Load data from Athena into SageMaker
import awswrangler as wr

df = wr.athena.read_sql_query(
    sql="SELECT * FROM real_estate_db.tokyo_properties WHERE year='2024'",
    database="real_estate_db",
    workgroup="real-estate-analysis"
)
```

### Redshift Spectrum

```sql
-- Create external schema in Redshift
CREATE EXTERNAL SCHEMA real_estate_spectrum
FROM DATA CATALOG
DATABASE 'real_estate_db'
IAM_ROLE 'arn:aws:iam::123456789012:role/RedshiftSpectrumRole';

-- Query from Redshift
SELECT * FROM real_estate_spectrum.tokyo_properties LIMIT 10;
```

## Maintenance

### Update Crawler Schedule

```bash
aws glue update-crawler \
  --name real-estate-crawler \
  --schedule "cron(0 2 * * ? *)"  # Daily at 2 AM UTC
```

### Monitor Query Costs

```bash
# Get workgroup metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Athena \
  --metric-name DataScannedInBytes \
  --dimensions Name=WorkGroup,Value=real-estate-analysis \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-31T23:59:59Z \
  --period 86400 \
  --statistics Sum
```

## Troubleshooting

### Common Issues

1. **Crawler finds no tables**
   - Check S3 bucket permissions
   - Verify data exists at the specified prefix
   - Check crawler logs in CloudWatch

2. **Query returns no results**
   - Verify table schema matches actual data
   - Check partition filters
   - Ensure data types are correct

3. **Permission denied errors**
   - Check IAM role has S3 access
   - Verify Athena workgroup permissions
   - Ensure query result location is accessible

### Debug Commands

```bash
# Check crawler logs
aws logs tail /aws-glue/crawlers --follow

# Describe table schema
aws glue get-table \
  --database-name real_estate_db \
  --name tokyo_properties

# Test S3 access
aws s3 ls s3://your-bucket-name/cleaned/tokyo/ --recursive
```

## Next Steps

1. Set up automated data quality checks
2. Create CloudWatch dashboards for monitoring
3. Implement cost allocation tags
4. Set up query result caching
5. Create materialized views for common queries