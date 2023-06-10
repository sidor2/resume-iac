from aws_cdk import (
    Stack,
    CfnOutput,
    RemovalPolicy,
    Token,
    aws_cloudfront_origins as origins,
    aws_cloudfront as cloudfront,
    aws_certificatemanager as acm,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_s3 as s3,
    aws_iam as iam,
    # core,
)

from constructs import Construct

class ImportedStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # import an existing cloudfront distribution
        cloudfront_distribution = cloudfront.Distribution.from_distribution_attributes(self,
            'ImportedCloudFront',
            domain_name='drcz31f1ewbce.cloudfront.net',
            distribution_id='E2DEPFBEJNVFOV',
        )

        webbucket = s3.Bucket.from_bucket_name(self, 'ImportedWebBucket', 'drcz31f1ewbce.s3.amazonaws.com')
        
                                                                                