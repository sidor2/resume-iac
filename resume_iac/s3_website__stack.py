from aws_cdk import (
    Arn,
    ArnComponents,
    ArnFormat,
    Duration,
    Stack,
    CfnOutput,
    RemovalPolicy,
    aws_cloudfront_origins as origins,
    aws_cloudfront as cloudfront,
    aws_certificatemanager as acm,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_s3 as s3,
    aws_iam as iam,
    aws_apigateway as apigateway
)

from constructs import Construct

def read_csp(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines]
            text_string = ' '.join(lines)
            return text_string
    except IOError:
        print(f"Error: Unable to read the file '{file_path}'.")


csp = read_csp('templates/csp.txt')


class S3WebsiteStack(Stack):

    def __init__(self, 
                scope: Construct, 
                id: str, 
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
        hosted_zone = route53.HostedZone.from_lookup(self,"HostedZone", 
            domain_name=domain_name
        )

        # Create an ACM certificate for the custom domain
        certificate_validation = acm.CertificateValidation.from_dns(
            hosted_zone=hosted_zone
        )

        certificate = acm.Certificate(self, "Certificate",
            domain_name=domain_name,
            subject_alternative_names=[f"www.{domain_name}"],
            validation=certificate_validation
        )

        oac_config = cloudfront.CfnOriginAccessControl.OriginAccessControlConfigProperty(
            name="webbucket",
            origin_access_control_origin_type="s3",
            signing_behavior="always",
            signing_protocol="sigv4"
        )

        oac = cloudfront.CfnOriginAccessControl(self, 
            "BucketOAC",
            origin_access_control_config=oac_config
        )

        cs_policy = cloudfront.ResponseHeadersContentSecurityPolicy(
            content_security_policy=f"{csp}", 
            override=True
        )
        
        ct_options = cloudfront.ResponseHeadersContentTypeOptions(override=True)
        
        frame_opt = cloudfront.ResponseHeadersFrameOptions(
            frame_option=cloudfront.HeadersFrameOption.DENY, 
            override=True
        )
        
        ref_policy = cloudfront.ResponseHeadersReferrerPolicy(
            referrer_policy=cloudfront.HeadersReferrerPolicy.NO_REFERRER, 
            override=True
        )

        hsts = cloudfront.ResponseHeadersStrictTransportSecurity(
            access_control_max_age=Duration.seconds(15768000), 
            include_subdomains=True, 
            override=True
        )
        
        xss_prot = cloudfront.ResponseHeadersXSSProtection(
            protection=True, 
            mode_block=True, 
            override=True
        )

        security_headers = cloudfront.ResponseSecurityHeadersBehavior(
            content_security_policy=cs_policy,
            content_type_options=ct_options,
            frame_options=frame_opt,
            referrer_policy=ref_policy,
            strict_transport_security=hsts,
            xss_protection=xss_prot
        )

        response_headers_policy=cloudfront.ResponseHeadersPolicy(self, 
            "ResponseHeadersPolicy",
            security_headers_behavior=security_headers
        )

        default_behave = cloudfront.BehaviorOptions(
            origin=origins.S3Origin(bucket),
            viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
            response_headers_policy=response_headers_policy,
            # TODO: enable cache for prod
            cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
        )

        not_found_res = cloudfront.ErrorResponse(
            http_status=404,
            response_http_status=404,
            response_page_path="/error.html",
            ttl=Duration.seconds(10)
        )

        not_auth_res = cloudfront.ErrorResponse(
            http_status=403,
            response_http_status=403,
            response_page_path="/error.html",
            ttl=Duration.seconds(10)
        )

        distribution = cloudfront.Distribution(self, "CloudFrontDistribution",
            default_behavior=default_behave,
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,
            certificate=certificate,
            domain_names=[f"www.{domain_name}",f"{domain_name}"],
            comment="CloudFront Distribution for the S3 Website",
            default_root_object="index.html",
            error_responses=[not_found_res, not_auth_res]
        )

        rest_api_origin = origins.RestApiOrigin(
            rest_api=rest_api,
            origin_path="/prod",
            custom_headers={"x-api-key": f"REPLACE ME WITH API KEY, ID {api_key.key_id }"}
        )

        distribution.add_behavior(
            path_pattern="/counter",
            origin = rest_api_origin,
            viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
            origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER_EXCEPT_HOST_HEADER
        )
        
        arn_components = ArnComponents(
            service="cloudfront",
            resource="distribution",
            resource_name=distribution.distribution_id,
            arn_format=ArnFormat.SLASH_RESOURCE_NAME,
            region=""
        )

        dist_arn = Arn.format(
            arn_components,
            self
        )
        
        allow_s3_statement = iam.PolicyStatement(
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

        bucket.add_to_resource_policy(
            allow_s3_statement
        )

        ## clean-up the OAI reference and associate the OAC with the cloudfront distribution 
        # query the site bucket policy as a document
        bucket_policy = bucket.policy
        bucket_policy_document = bucket_policy.document

        # remove the CloudFront Origin Access Identity permission from the bucket policy
        if isinstance(bucket_policy_document, iam.PolicyDocument):
            bucket_policy_document_json = bucket_policy_document.to_json()
            # create an updated policy without the OAI reference
            bucket_policy_updated_json = {'Version': '2012-10-17', 'Statement': []}
            for statement in bucket_policy_document_json['Statement']:
                if 'CanonicalUser' not in statement['Principal']:
                    bucket_policy_updated_json['Statement'].append(statement)

        # apply the updated bucket policy to the bucket
        bucket_policy_override = bucket.node.find_child("Policy").node.default_child
        bucket_policy_override.add_override('Properties.PolicyDocument', bucket_policy_updated_json)

        # remove the created OAI reference (S3 Origin property) for the distribution
        all_distribution_props = distribution.node.find_all()
        for child in all_distribution_props:
            if child.node.id == 'S3Origin':
                child.node.try_remove_child('Resource')

        # associate the created OAC with the distribution
        distribution_props = distribution.node.default_child
        distribution_props.add_override('Properties.DistributionConfig.Origins.0.S3OriginConfig.OriginAccessIdentity', '')
        distribution_props.add_property_override(
            "DistributionConfig.Origins.0.OriginAccessControlId",
            oac.ref
        )

        route53.CnameRecord(self, "CnameRecord",
            zone=hosted_zone,
            record_name=f"www.{domain_name}",
            domain_name=distribution.distribution_domain_name,
        )

        route53.ARecord(self, "RootAlias",
            zone=hosted_zone,
            record_name=f"{domain_name}",
            target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(distribution))
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
