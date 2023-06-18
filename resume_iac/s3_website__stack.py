from aws_cdk import (
    ArnFormat,
    Duration,
    Stack,
    CfnOutput,
    RemovalPolicy,
    aws_cloudfront_origins as origins,
    aws_cloudfront as cloudfront,
    aws_certificatemanager as acm,
    aws_route53 as route53,
    aws_s3 as s3,
    aws_iam as iam,
    Arn,
    ArnComponents,
    aws_apigateway as apigateway
)

from constructs import Construct

def read_file_and_convert_to_string(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines]
            text_string = ' '.join(lines)
            return text_string
    except IOError:
        print(f"Error: Unable to read the file '{file_path}'.")


file_path = 'templates/csp.txt'
csp = read_file_and_convert_to_string(file_path)


class S3WebsiteStack(Stack):

    def __init__(self, scope: Construct, id: str, 
                domain_name: str, 
                rest_api: apigateway.RestApi,
                api_key: apigateway.ApiKey, 
                **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create the S3 bucket
        bucket = s3.Bucket(self, "WebsiteBucket",
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

        cfn_origin_access_control = cloudfront.CfnOriginAccessControl(self, "BucketOAC",
            origin_access_control_config=cloudfront.CfnOriginAccessControl.OriginAccessControlConfigProperty(
                name="webbucket",
                origin_access_control_origin_type="s3",
                signing_behavior="always",
                signing_protocol="sigv4"
            ),
        )

# TODO: add a custom error page to the distribution

        response_headers_policy=cloudfront.ResponseHeadersPolicy(self, "ResponseHeadersPolicy",
            security_headers_behavior=cloudfront.ResponseSecurityHeadersBehavior(
                content_security_policy=cloudfront.ResponseHeadersContentSecurityPolicy(
                    content_security_policy=f"{csp}", 
                        override=True
                    ),
                content_type_options=cloudfront.ResponseHeadersContentTypeOptions(override=True),
                frame_options=cloudfront.ResponseHeadersFrameOptions(frame_option=cloudfront.HeadersFrameOption.DENY, override=True),
                referrer_policy=cloudfront.ResponseHeadersReferrerPolicy(referrer_policy=cloudfront.HeadersReferrerPolicy.NO_REFERRER, override=True),
                strict_transport_security=cloudfront.ResponseHeadersStrictTransportSecurity(access_control_max_age=Duration.seconds(15768000), include_subdomains=True, override=True),
                xss_protection=cloudfront.ResponseHeadersXSSProtection(protection=True, mode_block=True, override=True)
            )
        )

        distribution = cloudfront.Distribution(self, "CloudFrontDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                response_headers_policy=response_headers_policy,
                # TODO: enable cache for prod
                cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
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
                origin_path="/prod",
                custom_headers={"x-api-key": f"REPLACE ME WITH API KEY ID {api_key.key_id }"}
            ),
            viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
            origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER_EXCEPT_HOST_HEADER
                
        )
        
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
       