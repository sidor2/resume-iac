from aws_cdk import (
    ArnFormat,
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
    Arn,
    ArnComponents,
    aws_apigateway as apigateway
)

from constructs import Construct

class S3WebsiteStack(Stack):

    def __init__(self, scope: Construct, id: str, 
                domain_name: str, 
                rest_api: apigateway.RestApi, 
                **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create the S3 bucket
        bucket = s3.Bucket(self, "WebsiteBucket",
            # website_index_document="index.html",
            # website_error_document="error.html",
            public_read_access=False,
            enforce_ssl=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # Import the existing Route 53 hosted zone for the custom domain
        hosted_zone = route53.HostedZone.from_lookup(self, "HostedZone", domain_name=domain_name)

        # Create an ACM certificate for the custom domain
        certificate = acm.Certificate(self, "Certificate",
            domain_name=domain_name,
            subject_alternative_names=[f"www.{domain_name}"],
            validation=acm.CertificateValidation.from_dns(hosted_zone=hosted_zone)
        )

        # Create a CloudFront distribution for the S3 bucket

        # Create an Origin Access Identity for the CloudFront distribution
        # origin_access_identity = cloudfront.OriginAccessIdentity(self, "OriginAccessIdentity")


        cfn_origin_access_control = cloudfront.CfnOriginAccessControl(self, "BucketOAC",
            origin_access_control_config=cloudfront.CfnOriginAccessControl.OriginAccessControlConfigProperty(
                name="webbucket",
                origin_access_control_origin_type="s3",
                signing_behavior="always",
                signing_protocol="sigv4"
            )
        )

        distribution = cloudfront.Distribution(self, "CloudFrontDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                # origin=origins.HttpOrigin(
                #     bucket.bucket_website_domain_name,
                #     # https_port=443,
                #     origin_ssl_protocols=[cloudfront.OriginSslPolicy.TLS_V1_2]
                # )
            ),
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,
            certificate=certificate,
            domain_names=[f"www.{domain_name}"],
            comment="CloudFront Distribution for the S3 Website",
            default_root_object="index.html",
        )

        distribution.add_behavior(
            path_pattern="/counter",
            origin = origins.RestApiOrigin(
                rest_api=rest_api,
                origin_path="/prod/counter",
            )
        )

        # Grant read access to the bucket for the CloudFront distribution
        # bucket.grant_read(origin_access_identity)
        
        dist_arn = Arn.format(
            ArnComponents(
                service="cloudfront",
                resource="distribution",
                resource_name=distribution.distribution_id,
                arn_format=ArnFormat.SLASH_RESOURCE_NAME,
                region=""
            ),
            self
        )

        bucket.add_to_resource_policy(
            iam.PolicyStatement(
                actions=[
                    "s3:GetBucket*",
                    "s3:GetObject*",
                    "s3:List*"  
                ],
                resources=[
                    bucket.bucket_arn,
                    bucket.arn_for_objects("*")
                ],
                principals=[iam.ServicePrincipal("cloudfront.amazonaws.com")],
                effect=iam.Effect.ALLOW,
                conditions={
                    "StringEquals": {
                    "AWS:SourceArn": f"{dist_arn}"
                    }
                }
            )
        )


        # Create the CloudFront distribution
        # distribution = cloudfront.CloudFrontWebDistribution(self, "CloudFrontWebDistribution",
        #     origin_configs=[
        #         cloudfront.SourceConfiguration(
        #             s3_origin_source=cloudfront.S3OriginConfig(
        #                 s3_bucket_source=bucket,
        #                 # origin_access_identity=origin_access_identity,
        #                 ),
        #             behaviors=[cloudfront.Behavior(
        #                     is_default_behavior=True,                             
        #                 )
        #             ]
        #         )
        #     ],
        #     viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        #     price_class=cloudfront.PriceClass.PRICE_CLASS_100,
        #     viewer_certificate=cloudfront.ViewerCertificate.from_acm_certificate(
        #         certificate=certificate,
        #         aliases=[f"www.{domain_name}"],
        #     ),
        #     comment="CloudFront Distribution for the S3 Website",
        # )


        route53.CnameRecord(self, "CnameRecord",
            zone=hosted_zone,
            record_name=f"www.{domain_name}",
            domain_name=distribution.distribution_domain_name,
        )


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

        # output the distribution id
        CfnOutput(self, "DistributionId",
            value=distribution.distribution_id,
            description="Distribution Id"
        )
       