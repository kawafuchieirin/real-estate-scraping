#!/bin/bash

# Real Estate Data Analysis Infrastructure Deployment Script
# This script deploys the AWS Glue and Athena infrastructure for analyzing real estate data

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
STACK_NAME="real-estate-glue-athena"
TABLE_STACK_NAME="real-estate-table-schema"
REGION=${AWS_REGION:-"ap-northeast-1"}
S3_BUCKET=""
DATA_PREFIX="cleaned/tokyo/"
DEPLOY_TABLES=false

# Function to print colored output
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if stack exists
stack_exists() {
    aws cloudformation describe-stacks --stack-name $1 --region $REGION >/dev/null 2>&1
}

# Function to wait for stack operation
wait_for_stack() {
    local stack_name=$1
    local operation=$2
    
    print_message $YELLOW "⏳ Waiting for stack $operation to complete..."
    
    aws cloudformation wait stack-${operation}-complete \
        --stack-name $stack_name \
        --region $REGION
    
    if [ $? -eq 0 ]; then
        print_message $GREEN "✅ Stack $operation completed successfully!"
    else
        print_message $RED "❌ Stack $operation failed!"
        exit 1
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --bucket)
            S3_BUCKET="$2"
            shift 2
            ;;
        --prefix)
            DATA_PREFIX="$2"
            shift 2
            ;;
        --region)
            REGION="$2"
            shift 2
            ;;
        --deploy-tables)
            DEPLOY_TABLES=true
            shift
            ;;
        --help)
            echo "Usage: $0 --bucket <s3-bucket-name> [options]"
            echo ""
            echo "Options:"
            echo "  --bucket         S3 bucket name (required)"
            echo "  --prefix         S3 prefix for data (default: cleaned/tokyo/)"
            echo "  --region         AWS region (default: ap-northeast-1)"
            echo "  --deploy-tables  Also deploy explicit table definitions"
            echo "  --help           Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Validate required parameters
if [ -z "$S3_BUCKET" ]; then
    print_message $RED "❌ Error: S3 bucket name is required!"
    echo "Use: $0 --bucket <bucket-name>"
    exit 1
fi

print_message $GREEN "🚀 Real Estate Data Analysis Infrastructure Deployment"
echo "=================================================="
echo "S3 Bucket: $S3_BUCKET"
echo "Data Prefix: $DATA_PREFIX"
echo "Region: $REGION"
echo "Deploy Tables: $DEPLOY_TABLES"
echo "=================================================="
echo ""

# Check AWS CLI is installed
if ! command -v aws &> /dev/null; then
    print_message $RED "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity --region $REGION >/dev/null 2>&1; then
    print_message $RED "❌ AWS credentials not configured or invalid."
    exit 1
fi

# Deploy main infrastructure stack
print_message $YELLOW "📦 Deploying main infrastructure stack..."

if stack_exists $STACK_NAME; then
    print_message $YELLOW "Stack $STACK_NAME already exists. Updating..."
    aws cloudformation update-stack \
        --stack-name $STACK_NAME \
        --template-body file://glue-athena-stack.yaml \
        --parameters \
            ParameterKey=S3BucketName,ParameterValue=$S3_BUCKET \
            ParameterKey=DataPrefix,ParameterValue=$DATA_PREFIX \
        --capabilities CAPABILITY_NAMED_IAM \
        --region $REGION
    
    wait_for_stack $STACK_NAME "update"
else
    print_message $YELLOW "Creating new stack $STACK_NAME..."
    aws cloudformation create-stack \
        --stack-name $STACK_NAME \
        --template-body file://glue-athena-stack.yaml \
        --parameters \
            ParameterKey=S3BucketName,ParameterValue=$S3_BUCKET \
            ParameterKey=DataPrefix,ParameterValue=$DATA_PREFIX \
        --capabilities CAPABILITY_NAMED_IAM \
        --region $REGION
    
    wait_for_stack $STACK_NAME "create"
fi

# Deploy table schema stack if requested
if [ "$DEPLOY_TABLES" = true ]; then
    print_message $YELLOW "📦 Deploying table schema stack..."
    
    if stack_exists $TABLE_STACK_NAME; then
        print_message $YELLOW "Stack $TABLE_STACK_NAME already exists. Updating..."
        aws cloudformation update-stack \
            --stack-name $TABLE_STACK_NAME \
            --template-body file://glue-table-schema.yaml \
            --parameters \
                ParameterKey=S3BucketName,ParameterValue=$S3_BUCKET \
                ParameterKey=DataPrefix,ParameterValue=$DATA_PREFIX \
            --region $REGION
        
        wait_for_stack $TABLE_STACK_NAME "update"
    else
        print_message $YELLOW "Creating new stack $TABLE_STACK_NAME..."
        aws cloudformation create-stack \
            --stack-name $TABLE_STACK_NAME \
            --template-body file://glue-table-schema.yaml \
            --parameters \
                ParameterKey=S3BucketName,ParameterValue=$S3_BUCKET \
                ParameterKey=DataPrefix,ParameterValue=$DATA_PREFIX \
            --region $REGION
        
        wait_for_stack $TABLE_STACK_NAME "create"
    fi
fi

# Get stack outputs
print_message $YELLOW "📋 Getting stack outputs..."
CRAWLER_NAME=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`GlueCrawlerName`].OutputValue' \
    --output text \
    --region $REGION)

DATABASE_NAME=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`GlueDatabaseName`].OutputValue' \
    --output text \
    --region $REGION)

WORKGROUP_NAME=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`AthenaWorkGroupName`].OutputValue' \
    --output text \
    --region $REGION)

# Run the crawler
print_message $YELLOW "🕷️  Starting Glue Crawler..."
aws glue start-crawler --name $CRAWLER_NAME --region $REGION

print_message $GREEN "✅ Deployment completed successfully!"
echo ""
print_message $GREEN "📊 Next Steps:"
echo "1. Wait for the crawler to complete (check status with: aws glue get-crawler --name $CRAWLER_NAME)"
echo "2. Open Athena console and select workgroup: $WORKGROUP_NAME"
echo "3. Select database: $DATABASE_NAME"
echo "4. Run queries from the athena-queries/ directory"
echo ""
print_message $YELLOW "💡 Example query:"
echo "aws athena start-query-execution \\"
echo "  --query-string \"SELECT COUNT(*) FROM ${DATABASE_NAME}.tokyo_properties\" \\"
echo "  --work-group $WORKGROUP_NAME \\"
echo "  --query-execution-context Database=$DATABASE_NAME"