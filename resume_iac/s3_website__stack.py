from aws_cdk import (
    Stack,
    CfnOutput,
    RemovalPolicy,
    Token,
    aws_cloudfront as cloudfront,
    aws_certificatemanager as acm,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_s3 as s3,
    aws_iam as iam,
    # core,
)

from constructs import Construct

class S3WebsiteStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        domain_name = "cmcloudlab1780.info"

        # Create the S3 bucket
        bucket = s3.Bucket(self, "WebsiteBucket",
            website_index_document="index.html",
            website_error_document="error.html",
            public_read_access=False,
            enforce_ssl=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Import the existing Route 53 hosted zone for the custom domain
        hosted_zone = route53.HostedZone.from_lookup(self, "HostedZone", domain_name=domain_name)

        # Create an ACM certificate for the custom domain
        certificate = acm.Certificate(self, "Certificate",
            domain_name=domain_name,
            subject_alternative_names=[f"www.{domain_name}"],
            validation=acm.CertificateValidation.from_dns(hosted_zone=hosted_zone)
        )

        # Create an Origin Access Identity for the CloudFront distribution
        origin_access_identity = cloudfront.OriginAccessIdentity(self, "OriginAccessIdentity")

        # Create the CloudFront distribution
        distribution = cloudfront.CloudFrontWebDistribution(self, "CloudFrontDistribution",
            origin_configs=[
                cloudfront.SourceConfiguration(
                    s3_origin_source=cloudfront.S3OriginConfig(
                        s3_bucket_source=bucket,
                        origin_access_identity=origin_access_identity
                        ),
                    behaviors=[cloudfront.Behavior(is_default_behavior=True)]
                )
            ],
            viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            price_class=cloudfront.PriceClass.PRICE_CLASS_ALL,
            viewer_certificate=cloudfront.ViewerCertificate.from_acm_certificate(
                certificate=certificate,
                # ssl_support_method=cloudfront.SSLMethod.SNI,
                aliases=[f"www.{domain_name}"],
            )
        )


        # Create an alias record in Route 53 to point to the CloudFront distribution
        # route53.ARecord(self, "AliasRecord",
        #     zone=hosted_zone,
        #     target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(distribution)),
        #     record_name="cmcloudlab627.info"
        # )

        route53.CnameRecord(self, "CnameRecord",
            zone=hosted_zone,
            record_name=f"www.{domain_name}",
            domain_name=distribution.distribution_domain_name,
        )

        # Grant read access to the bucket for the CloudFront distribution
        bucket.grant_read(origin_access_identity)

        # Output the CloudFront domain name
        CfnOutput(self, "CloudFrontDomainName",
            value=distribution.distribution_domain_name,
            description="CloudFront Domain Name"
        )

        #Output the custom domain name
        CfnOutput(self, "CustomDomainName",
            value=f"www.{domain_name}",
            description="Custom Domain Name"
        )

