#!/usr/bin/env python3
import os

import aws_cdk as cdk
from resume_iac.imported import ImportedStack

from resume_iac.s3_website__stack import S3WebsiteStack
from resume_iac.apigw_ddb_lambda_stack import ApiDdbLambdaStack



app = cdk.App()



domain_name = "cmcloudlab1707.info"

api_ddb_lambda = ApiDdbLambdaStack(app, "ApiGwDdbStack",
    domain_name=domain_name,
    env=cdk.Environment(
        account=os.environ["CDK_DEFAULT_ACCOUNT"],
        region=os.environ["CDK_DEFAULT_REGION"]
    ),
)

S3WebsiteStack(app, "S3WebsiteStack",
    domain_name=domain_name,
    env=cdk.Environment(
        account=os.environ["CDK_DEFAULT_ACCOUNT"], 
        region=os.environ["CDK_DEFAULT_REGION"]
    ),
    rest_api=api_ddb_lambda.rest_api,
)



app.synth()
