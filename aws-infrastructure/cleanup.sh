#!/bin/bash

# Real Estate Data Analysis Infrastructure Cleanup Script
# This script removes the AWS Glue and Athena infrastructure

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
FORCE=false

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

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --region)
            REGION="$2"
            shift 2
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --region  AWS region (default: ap-northeast-1)"
            echo "  --force   Skip confirmation prompt"
            echo "  --help    Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

print_message $YELLOW "🗑️  Real Estate Data Analysis Infrastructure Cleanup"
echo "=================================================="
echo "Region: $REGION"
echo "Stacks to remove:"
echo "  - $STACK_NAME"
echo "  - $TABLE_STACK_NAME"
echo "=================================================="
echo ""

# Confirmation prompt
if [ "$FORCE" != true ]; then
    print_message $YELLOW "⚠️  Warning: This will delete all infrastructure resources!"
    read -p "Are you sure you want to continue? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        print_message $RED "Cleanup cancelled."
        exit 0
    fi
fi

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

# Function to delete stack
delete_stack() {
    local stack_name=$1
    
    if stack_exists $stack_name; then
        print_message $YELLOW "🗑️  Deleting stack: $stack_name..."
        
        aws cloudformation delete-stack \
            --stack-name $stack_name \
            --region $REGION
        
        print_message $YELLOW "⏳ Waiting for stack deletion to complete..."
        
        aws cloudformation wait stack-delete-complete \
            --stack-name $stack_name \
            --region $REGION
        
        if [ $? -eq 0 ]; then
            print_message $GREEN "✅ Stack $stack_name deleted successfully!"
        else
            print_message $RED "❌ Failed to delete stack $stack_name"
            return 1
        fi
    else
        print_message $YELLOW "Stack $stack_name does not exist, skipping..."
    fi
}

# Delete table schema stack first (if it exists)
delete_stack $TABLE_STACK_NAME

# Delete main infrastructure stack
delete_stack $STACK_NAME

print_message $GREEN "✅ Cleanup completed successfully!"
echo ""
print_message $YELLOW "📝 Note: S3 data and Athena query results are NOT deleted."
echo "To remove S3 data, use:"
echo "  aws s3 rm s3://your-bucket-name/cleaned/ --recursive"
echo "  aws s3 rm s3://your-bucket-name/athena-results/ --recursive"