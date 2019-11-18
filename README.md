# Created S3 Object Downloader

This CLI tool polls SQS queue for new object created events published by S3, and then it downloads objects to specified path.

## Policies

### AWS Managed Policy

- AmazonS3ReadOnlyAccess

### Inline Policies

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sqs:DeleteMessage",
                "sqs:ReceiveMessage"
            ],
            "Resource": "arn:aws:sqs:REGION:ACCOUNT-ID:QUEUE-NAME"
        }
    ]
}
```
