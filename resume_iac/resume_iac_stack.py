from aws_cdk import (
    # Duration,
    Stack,
    RemovalPolicy,
    # aws_sqs as sqs,
    aws_s3 as s3,
)
from constructs import Construct

class ResumeIacStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        web_bucket = s3.Bucket(self, "WebBucket",
                               bucket_name="resume-iac-web-bucket",
                               removal_policy=RemovalPolicy.DESTROY,
                               auto_delete_objects=True)

