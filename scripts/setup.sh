#!/bin/bash
# Setup LocalStack

echo "Starting LocalStack..."

localstack start -d

echo "Creating S3 bucket..."
aws --endpoint-url=http://localhost:4566 s3 mb s3://csv-bucket

echo "Creating DynamoDB table..."
aws --endpoint-url=http://localhost:4566 dynamodb create-table     --table-name CSVMetadata     --attribute-definitions AttributeName=filename,AttributeType=S     --key-schema AttributeName=filename,KeyType=HASH     --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1

echo "Creating SNS Topic..."
aws --endpoint-url=http://localhost:4566 sns create-topic --name CSVProcessingTopic

echo "Setup Complete!"
