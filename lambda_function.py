import json
import os
import boto3
import pandas as pd
import logging
from datetime import datetime
from botocore.exceptions import NoCredentialsError, ClientError

# Environment Variables
LOCALSTACK_ENDPOINT = os.getenv("LOCALSTACK_ENDPOINT", "http://localhost:4566")
S3_BUCKET = os.getenv("S3_BUCKET", "csv-bucket")
DYNAMO_TABLE = os.getenv("DYNAMO_TABLE", "CSVMetadata")
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN", "arn:aws:sns:us-east-1:000000000000:CSVProcessingTopic")

# AWS Clients (LocalStack)
s3_client = boto3.client("s3", endpoint_url=LOCALSTACK_ENDPOINT)
dynamodb = boto3.resource("dynamodb", endpoint_url=LOCALSTACK_ENDPOINT)
sns_client = boto3.client("sns", endpoint_url=LOCALSTACK_ENDPOINT)
table = dynamodb.Table(DYNAMO_TABLE)

# Logger Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_csv_metadata(bucket: str, key: str) -> dict:
    """Extract metadata from CSV stored in S3."""
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        file_size = response["ContentLength"]
        data = response["Body"].read().decode("utf-8")

        # Read CSV using Pandas (streaming for large files)
        df = pd.read_csv(pd.compat.StringIO(data), low_memory=False)

        metadata = {
            "filename": key,
            "upload_timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "file_size_bytes": file_size,
            "row_count": len(df),
            "column_count": len(df.columns),
            "column_names": list(df.columns),
        }

        logger.info(f"Extracted Metadata: {metadata}")
        return metadata

    except Exception as e:
        logger.error(f"Error extracting CSV metadata: {e}")
        raise

def store_metadata(metadata: dict):
    """Store extracted metadata in DynamoDB."""
    try:
        table.put_item(Item=metadata)
        logger.info("Metadata successfully stored in DynamoDB.")
    except Exception as e:
        logger.error(f"Error storing metadata in DynamoDB: {e}")
        raise

def send_sns_notification(metadata: dict):
    """Send SNS notification on successful processing."""
    try:
        message = {
            "Subject": "CSV Processing Complete",
            "Message": json.dumps(metadata, indent=4),
            "TopicArn": SNS_TOPIC_ARN
        }
        sns_client.publish(**message)
        logger.info("SNS notification sent.")
    except ClientError as e:
        logger.warning(f"SNS Notification Failed: {e}")

def lambda_handler(event, context):
    """AWS Lambda handler function."""
    try:
        record = event["Records"][0]
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        logger.info(f"Processing CSV: {key} from bucket: {bucket}")

        metadata = extract_csv_metadata(bucket, key)
        store_metadata(metadata)
        send_sns_notification(metadata)

        return {"statusCode": 200, "body": json.dumps(metadata)}

    except KeyError:
        logger.error("Invalid event format.")
        return {"statusCode": 400, "body": "Invalid event format"}

    except NoCredentialsError:
        logger.error("AWS credentials missing.")
        return {"statusCode": 500, "body": "AWS credentials missing"}

    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        return {"statusCode": 500, "body": str(e)}
