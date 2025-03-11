import os

LOCALSTACK_ENDPOINT = os.getenv("LOCALSTACK_ENDPOINT", "http://localhost:4566")
S3_BUCKET = os.getenv("S3_BUCKET", "csv-bucket")
DYNAMO_TABLE = os.getenv("DYNAMO_TABLE", "CSVMetadata")
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN", "arn:aws:sns:us-east-1:000000000000:CSVProcessingTopic")
