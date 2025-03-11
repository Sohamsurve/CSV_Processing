# CSV Processing Pipeline with LocalStack

## Overview
This project implements a serverless pipeline using **AWS Lambda, S3, and DynamoDB** (simulated using LocalStack). 
It processes CSV files uploaded to an S3 bucket, extracts metadata, stores it in DynamoDB, and optionally sends an SNS notification.

## Features
- Automatically triggers Lambda when a CSV file is uploaded.
- Extracts metadata (row count, column names, file size, etc.).
- Stores metadata in DynamoDB.
- Sends SNS notifications on completion (optional).
- Fully local development using LocalStack (no real AWS costs).

---

## 🚀 Setup Instructions

### 1️⃣ Install Dependencies
Ensure you have Python 3.9+ and LocalStack installed.
```bash
pip install boto3 pandas localstack awscli-local
```

### 2️⃣ Start LocalStack
```bash
localstack start -d
```

### 3️⃣ Create Required AWS Resources in LocalStack

#### Create S3 Bucket
```bash
aws --endpoint-url=http://localhost:4566 s3 mb s3://csv-bucket
```

#### Create DynamoDB Table
```bash
aws --endpoint-url=http://localhost:4566 dynamodb create-table     --table-name CSVMetadata     --attribute-definitions AttributeName=filename,AttributeType=S     --key-schema AttributeName=filename,KeyType=HASH     --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1
```

#### Create SNS Topic (Optional)
```bash
aws --endpoint-url=http://localhost:4566 sns create-topic --name CSVProcessingTopic
```

---

## 🚀 Deploying the Lambda Function

### 1️⃣ Package Lambda
```bash
zip function.zip lambda_function.py config.py
```

### 2️⃣ Deploy Lambda to LocalStack
```bash
aws --endpoint-url=http://localhost:4566 lambda create-function --function-name ProcessCSV     --runtime python3.9 --handler lambda_function.lambda_handler     --role arn:aws:iam::000000000000:role/lambda-role     --zip-file fileb://function.zip
```

### 3️⃣ Configure S3 to Trigger Lambda
```bash
aws --endpoint-url=http://localhost:4566 s3api put-bucket-notification-configuration --bucket csv-bucket --notification-configuration '{
    "LambdaFunctionConfigurations": [{
        "LambdaFunctionArn": "arn:aws:lambda:us-east-1:000000000000:function:ProcessCSV",
        "Events": ["s3:ObjectCreated:*"]
    }]
}'
```

---

## 🔬 Testing the System

### 1️⃣ Upload CSV File to S3
```bash
aws --endpoint-url=http://localhost:4566 s3 cp test.csv s3://csv-bucket/
```

### 2️⃣ Verify Metadata in DynamoDB
```bash
aws --endpoint-url=http://localhost:4566 dynamodb scan --table-name CSVMetadata
```

### 3️⃣ Check Lambda Logs
```bash
docker logs $(docker ps | grep localstack | awk '{print $1}')
```

---

## 📌 What’s Next?
✅ Extend the system with APIs (Flask/FastAPI) for querying metadata.  
✅ Build a UI Dashboard (React.js/Vue.js) to visualize processed CSVs.  
✅ Deploy on Docker for portability.  

---
